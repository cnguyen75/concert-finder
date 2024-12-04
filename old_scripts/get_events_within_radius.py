import pandas as pd
from geopy.distance import geodesic
from get_music_events import save_events_to_csv, handle_ambiguous_city

api_key = 'SVIWSxowXKKfzsXFqkAbVWd8NAmZeDns'
event_url = 'https://app.ticketmaster.com/discovery/v2/events.json'

def get_cities_within_radius(input_city, radius):
    """
    Find all cities within a given radius of the input city.
    
    Args:
        input_city (str): The name of the input city.
        radius (float): Radius in miles.
        cities_file (str): Path to the CSV file containing city, lat, and lng data.
    
    Returns:
        list: A list of city names within the radius.
    """
    # Load city data
    cities_df = pd.read_csv('uscities.csv')
    
    # Get the coordinates of the input city
    input_city_data = cities_df[cities_df['city'].str.lower() == input_city.lower()]
    if input_city_data.empty:
        raise ValueError(f"City '{input_city}' not found in the dataset.")
    
    input_coords = (input_city_data.iloc[0]['lat'], input_city_data.iloc[0]['lng'])
    
    # Calculate distances to other cities
    cities_within_radius = []
    for _, row in cities_df.iterrows():
        city_coords = (row['lat'], row['lng'])
        distance = geodesic(input_coords, city_coords).miles
        if distance <= radius:
            cities_within_radius.append(row['city'])
    
    return cities_within_radius

def get_events_nearby(input_city, input_state, radius):
    """
    Fetch music events in cities within a given radius of the input city.
    
    Args:
        input_city (str): The name of the input city.
        radius (float): Radius in miles.
        cities_file (str): Path to the CSV file containing city, lat, and lng data.
        api_key (str): Ticketmaster API key.
    """
    print(f"Finding cities within {radius} miles of {input_city}...")
    try:
        nearby_cities = get_cities_within_radius(input_city, radius)
    except ValueError as e:
        print(e)
        return
    
    print(f"Cities found: {', '.join(nearby_cities)}")
    
    all_events = []
    for city in nearby_cities:
        # Fetch events for each city
        print(f"Fetching events for {city}...")
        events = handle_ambiguous_city(city, input_state, api_key)  # Reuse existing logic
        all_events.extend(events)
    
    if all_events:
        print(f"Found {len(all_events)} events. Saving results...")
        save_events_to_csv(all_events, input_city)
    else:
        print("No events found in the specified radius.")
        
    return all_events

# Example usage
if __name__ == "__main__":
    city = input("Enter the city: ")
    state = input("Enter the state initials (CA for example):  ")
    radius = float(input("Enter the radius in miles: "))
    CITIES_FILE = "uscities.csv"  # Path to your CSV file with city data
    
    events = get_events_nearby(city, state, radius)
    if events:
        print(f"Upcoming events in {city}:")
        for event in events:
            print(f"Event: {event[0]}, Date: {event[1]}, City: {event[2]}, State: {event[3]}")
        
        #save_events_to_csv(events, city)
    else:
        print("No events to save.")
