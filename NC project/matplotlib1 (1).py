import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import plotly.graph_objects as go
from datetime import timedelta
import numpy as np

# Aircraft data dictionary
aircraft_data = {
    'Airbus_A320': {
        'name': 'Airbus A320',
        'max_takeoff_weight': 78000,  # kg
        'max_fuel_capacity': 24210,  # liters
        'max_range': 6900000,  # meters
        'engine_type': 'CFM International CFM56',
        'no_of_engines': 2,
        'cruise_speed': 281.46,  # m / s
        'max_speed': 288.12,  # m / s
        'fuel_consumption_rate': 0.78,  # kg / s
        'cargo_capacity': 37.4,  # m^3
        'wing_span': 35.8,  # meters
        'aircraft_length': 44.5,  # meters
        'aircraft_height': 12.5,  # meters
        'passenger_capacity': 186,
        'climb_rate': 12.32,  # m / s
        'descent_rate': 7.5,  # m / s
        'cruise_altitude': 12000  # meters
    },
    'Boeing_777': {
        'name': 'Boeing 777',
        'max_takeoff_weight': 347000,  # kg
        'max_fuel_capacity': 181280,  # liters
        'max_range': 15843000,  # meters
        'engine_type': 'General Electric GE90, Rolls-Royce Trent 800',
        'no_of_engines': 2,
        'cruise_speed': 305.17,  # m / s
        'max_speed': 315.56,  # m / s
        'fuel_consumption_rate': 1.94,  # kg / s
        'cargo_capacity': 25.3,  # m^3
        'wing_span': 64.8,  # meters
        'aircraft_length': 73.9,  # meters
        'aircraft_height': 18.6,  # meters
        'passenger_capacity': 396,
        'climb_rate': 20.27,  # m / s
        'descent_rate': 7.5,  # m / s
        'cruise_altitude': 11000  # meters
    },
    'Boeing_737': {
        'name': 'Boeing 737',
        'max_takeoff_weight': 85100,  # kg
        'max_fuel_capacity': 22000,  # liters
        'max_range': 5510000,  # meters
        'engine_type': 'CFM International CFM56',
        'no_of_engines': 2,
        'cruise_speed': 305.17,  # m / s
        'max_speed': 315.56,  # m / s
        'fuel_consumption_rate': 1.94,  # kg / s
        'cargo_capacity': 18.4,  # m^3
        'wing_span': 38.1,  # meters
        'aircraft_length': 39.5,  # meters
        'aircraft_height': 12.6,  # meters
        'passenger_capacity': 215,
        'climb_rate': 20.27,  # m / s
        'descent_rate': 7.5,  # m / s
        'cruise_altitude': 11000  # meters
    },
    'Airbus_A380': {
        'name': 'Airbus A380',
        'max_takeoff_weight': 560000,  # kg
        'max_fuel_capacity': 320000,  # liters
        'max_range': 15700000,  # meters
        'engine_type': 'Rolls-Royce Trent 900, Engine Alliance GP7200',
        'no_of_engines': 4,
        'cruise_speed': 292.35,  # m/s
        'max_speed': 306.14,  # m/s
        'fuel_consumption_rate': 3.33,  # kg/s
        'cargo_capacity': 34.8,  # m^3
        'wing_span': 79.8,  # meters
        'aircraft_length': 72.72,  # meters
        'aircraft_height': 24.1,  # meters
        'passenger_capacity': 853,
        'climb_rate': 20.27,  # m/s
        'descent_rate': 7.5,  # m/s
        'cruise_altitude': 13000  # meters
    }
}

def get_aircraft_choice():
    """Display aircraft choices and return the selected aircraft key."""
    st.title("Aircraft Prediction Model")

    aircraft_list = list(aircraft_data.keys())
    aircraft_names = [aircraft_data[key]['name'] for key in aircraft_list]
    choice = st.selectbox("Select your aircraft:", aircraft_names)
    return aircraft_list[aircraft_names.index(choice)]

def calculate_distance(fuel_consumed_liters, aircraft_key, wind_pressure, payload_weight):
    """Calculate the total distance and collect data for animation."""
    ac = aircraft_data[aircraft_key]

    # Convert fuel from liters to kg (assuming standard jet fuel density)
    fuel_consumed_kg = fuel_consumed_liters * 0.84

    # Extract necessary parameters from the aircraft dictionary
    cruise_altitude = ac['cruise_altitude']
    climb_rate = ac['climb_rate']
    descent_rate = ac['descent_rate']
    cruise_speed = ac['cruise_speed']
    base_fuel_consumption_rate = ac['fuel_consumption_rate']
    max_payload_capacity = ac['max_takeoff_weight'] - (ac['max_fuel_capacity'] * 0.84)

    # Adjust fuel consumption rate based on payload weight
    effective_fuel_consumption_rate = base_fuel_consumption_rate * (1 + (payload_weight / max_payload_capacity))

    # Data collection for animation
    time_points = []
    height_points = []
    distance_points = []

    current_time = 0
    current_height = 0
    current_distance = 0
    remaining_fuel_kg = fuel_consumed_kg

    # Climb phase
    climb_time = cruise_altitude / climb_rate
    climb_fuel_consumed = climb_time * effective_fuel_consumption_rate
    climb_distance = 0.5 * climb_time * cruise_speed  # Approximation of distance during climb

    if climb_fuel_consumed < remaining_fuel_kg:
        time_climb = np.linspace(0, climb_time, num=50)  # Use 50 points for smooth animation
        height_climb = time_climb * climb_rate
        distance_climb = time_climb * cruise_speed * 0.5
        for t, h, d in zip(time_climb, height_climb, distance_climb):
            time_points.append(current_time + t)
            height_points.append(h)
            distance_points.append(current_distance + d)
        
        # Update current values
        current_time += climb_time
        current_height = cruise_altitude
        current_distance += climb_distance
        remaining_fuel_kg -= climb_fuel_consumed
    else:
        raise ValueError("Fuel consumed exceeds the available capacity during climb")

    # Cruise phase
    cruise_fuel_consumed = remaining_fuel_kg
    cruise_time = cruise_fuel_consumed / effective_fuel_consumption_rate
    cruise_distance = cruise_time * cruise_speed

    # Apply wind pressure factor
    wind_pressure_factor = 1 - (wind_pressure / 100)
    cruise_distance *= wind_pressure_factor
    cruise_time *= wind_pressure_factor

    time_cruise = np.linspace(0, cruise_time, num=100)  # Use 100 points for smooth animation
    height_cruise = np.full_like(time_cruise, cruise_altitude)
    distance_cruise = current_distance + time_cruise * cruise_speed
    for t, h, d in zip(time_cruise, height_cruise, distance_cruise):
        time_points.append(current_time + t)
        height_points.append(h)
        distance_points.append(d)
    
    # Update current values
    current_time += cruise_time
    current_distance += cruise_distance

    # Descent phase
    descent_time = cruise_altitude / descent_rate
    descent_distance = 0.5 * descent_time * cruise_speed  # Approximation of distance during descent

    time_descent = np.linspace(0, descent_time, num=50)  # Use 50 points for smooth animation
    height_descent = cruise_altitude - time_descent * descent_rate
    distance_descent = current_distance + time_descent * cruise_speed * 0.5
    for t, h, d in zip(time_descent, height_descent, distance_descent):
        time_points.append(current_time + t)
        height_points.append(h)
        distance_points.append(d)
    
    # Update current values
    current_time += descent_time
    current_distance += descent_distance

    total_distance = current_distance
    total_time = current_time

    return total_distance, total_time, distance_points, height_points, time_points

def calculate_error(accurate_distance, calculated_distance):
    absolute_error = abs(accurate_distance - calculated_distance)
    percentage_error = (absolute_error / accurate_distance) * 100

    return absolute_error, percentage_error



# Function to format seconds into hours and minutes
def format_time(seconds):
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f'{hours:02}:{minutes:02}'

# Function to animate the flight path using Plotly
def animate_flight(distance_points, height_points, time_points, aircraft_name):
    fig = go.Figure()

    # Add initial trace for the flight path
    fig.add_trace(go.Scatter(x=distance_points, y=height_points, mode='lines', name='Flight Path', line=dict(color='blue', width=2)))

    # Set layout for the animation
    fig.update_layout(
        title=f'{aircraft_name} Flight Path Animation',
        xaxis_title='Distance (m)',
        yaxis_title='Height (m)',
        hovermode='closest',
        showlegend=False,  # Hide legend for cleaner look
        xaxis=dict(range=[0, max(distance_points)]),  # Adjust x-axis range to cover the full distance
        yaxis=dict(range=[0, max(height_points) + 1000])  # Adjust y-axis range to cover the full height plus some margin
    )

    frames = []
    # Create frames for animation
    for i in range(len(distance_points)):
        frame = go.Frame(
            data=[go.Scatter(
                x=distance_points[:i+1],
                y=height_points[:i+1],
                mode='lines',
                name='Flight Path',
                line=dict(color='blue', width=2),
                text=f'Time: {format_time(time_points[i])}',  # Display time in hours and minutes as hover text
            )],
            name=f'frame{i}'
        )
        frames.append(frame)

    # Add frames to the figure
    fig.frames = frames

    # Display the animated Plotly figure in Streamlit
    st.plotly_chart(fig)



def main():
    aircraft_key = get_aircraft_choice()
    aircraft = aircraft_data[aircraft_key]

    # Maximum fuel capacity in liters
    max_fuel_capacity = float(aircraft['max_fuel_capacity'])  # Ensure it is a float
    # Maximum payload weight in kg
    max_payload_weight = float(aircraft['max_takeoff_weight'] - (aircraft['max_fuel_capacity'] * 0.84))  # Ensure it is a float
    # Maximum range in meters
    max_range = float(aircraft['max_range'])  # Ensure it is a float

    # Input for fuel consumed with validation
    fuel_liters = st.number_input(
        f"Enter the amount of fuel consumed (in liters, max {max_fuel_capacity:.2f} L):",
        min_value=0.0, 
        max_value=max_fuel_capacity, 
        step=1.0
    )
    if fuel_liters > max_fuel_capacity:
        st.warning(f"The entered fuel consumption exceeds the maximum fuel capacity of {max_fuel_capacity:.2f} liters.")
        return

    # Input for wind pressure effect with validation
    wind_pressure = st.number_input(
        "Enter the wind pressure effect (as a percentage, e.g., 10 for 10%):",
        min_value=0.0, 
        max_value=100.0,  # Added max value for wind pressure
        step=1.0
    )
    if wind_pressure < 0 or wind_pressure > 100:
        st.warning("Wind pressure effect must be between 0 and 100 percent.")
        return

    # Input for payload weight with validation
    payload_weight = st.number_input(
        f"Enter the payload weight (in kg, max {max_payload_weight:.2f} kg):",
        min_value=0.0, 
        max_value=max_payload_weight, 
        step=1.0
    )
    if payload_weight > max_payload_weight:
        st.warning(f"The entered payload weight exceeds the maximum payload capacity of {max_payload_weight:.2f} kg.")
        return

    # Input for accurate distance with validation
    accurate_distance = st.number_input(
        f"Enter the accurate distance (in meters, max {max_range:.2f} m):",
        min_value=0.0, 
        max_value=max_range, 
        step=1.0
    )
    if accurate_distance > max_range:
        st.warning(f"The entered distance exceeds the maximum range of {max_range:.2f} meters.")
        return

    if st.button("Calculate Distance"):
        try:
            total_distance, total_time, distance_points, height_points, time_points = calculate_distance(
                fuel_liters, aircraft_key, wind_pressure, payload_weight)

            st.write(f"Aircraft: {aircraft['name']}")
            st.write(f"Total Distance: {total_distance:.2f} meters")
            st.write(f"Total Time: {total_time:.2f} seconds")

            absolute_error, percentage_error = calculate_error(accurate_distance, total_distance)

            st.write(f"Absolute Error: {absolute_error:.2f} meters")
            st.write(f"Percentage Error: {percentage_error:.2f}%")

            animate_flight(distance_points, height_points, time_points, aircraft['name'])

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
