import shutil
import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pywavefront
import math

# Function to modify OBJ file
def modify_obj_file(input_filename, output_filename):
    with open(input_filename, 'r') as file:
        lines = file.readlines()

    with open(output_filename, 'w') as file:
        for line in lines:
            if line.startswith('Tf ') or line.startswith('g ') or line.startswith('s '):
                file.write('# ' + line)  # Comment out the Tf, g, and s lines
            else:
                file.write(line)

# Modify the OBJ file
input_filename = 'airbus/11805_airplane_v2_L2.obj'
output_filename = 'airbus/11805_airplane_v2_L2_modified.obj'
modify_obj_file(input_filename, output_filename)

# Ensure the MTL file is in the same directory
mtl_input_filename = 'airbus/11805_airplane_v2_L2.mtl'
mtl_output_filename = 'airbus/11805_airplane_v2_L2_modified.mtl'
shutil.copyfile(mtl_input_filename, mtl_output_filename)

print(f"Modified OBJ file saved as {output_filename}")
print(f"MTL file copied to {mtl_output_filename}")

def load_model(filename):
    try:
        scene = pywavefront.Wavefront(filename, collect_faces=True)
        print(f"Successfully loaded model '{filename}'")
        return scene
    except Exception as e:
        print(f"Error loading model '{filename}': {e}")
        return None

def draw_model(scene):
    glBegin(GL_TRIANGLES)
    for mesh in scene.mesh_list:
        for face in mesh.faces:
            for vertex_i in face:
                glVertex3fv(scene.vertices[vertex_i])
    glEnd()
def update_orientation(start_position, landing_position):
    # Calculate direction vector
    direction_x = landing_position['x'] - start_position['x']
    direction_z = landing_position['z'] - start_position['z']
    
    # Calculate orientation angle
    if direction_x != 0:
        orientation_angle = math.degrees(math.atan2(direction_z, direction_x))
    else:
        orientation_angle = 90 if direction_z > 0 else -90  # Handle edge case for direction_x = 0

    # Apply rotation around y-axis (assuming initial aircraft orientation)
    glRotatef(orientation_angle, 0, 1, 0)
    
# Trajectory parameters
start_position = {'x': -100, 'y': 0, 'z': -100}  # Adjusted starting position
landing_position = {'x': 100, 'y': 0, 'z': -100}  # Adjusted landing position
total_distance = math.sqrt((landing_position['x'] - start_position['x'])**2 + (landing_position['z'] - start_position['z'])**2)
trajectory_speed = 0.3  # Increased speed further

# Initialize position and time
position = start_position.copy()
time_elapsed = 0

def update_position():
    global time_elapsed, position

    # Calculate position based on trajectory
    time_step = 0.1  # Adjust time step for smooth movement
    time_elapsed += time_step * trajectory_speed  # Adjusting speed here

    # Update position based on linear interpolation along the trajectory
    if time_elapsed <= 1.0:
        position['x'] = start_position['x'] + (landing_position['x'] - start_position['x']) * time_elapsed
        position['y'] = start_position['y']
        position['z'] = start_position['z'] + (landing_position['z'] - start_position['z']) * time_elapsed

    # Calculate orientation based on direction of movement
    orientation_angle = math.degrees(math.atan2(landing_position['z'] - start_position['z'], landing_position['x'] - start_position['x']))
    glRotatef(orientation_angle, 0, 1, 0)  # Rotate around y-axis
def main():
    pygame.init()
    display = (1300, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
    glTranslatef(0.0, 0.0, -100)

    # Load the modified Airbus A320 model
    model = load_model('airbus/11805_airplane_v2_L2_modified.obj')

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        update_position()  # Update the position along the trajectory
        update_orientation(start_position, landing_position)  # Update the orientation

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if model:
            glPushMatrix()
            glTranslatef(position['x'], position['y'], position['z'])
            glScalef(0.01, 0.01, 0.01)  # Adjust scale factor if needed
            draw_model(model)
            glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
