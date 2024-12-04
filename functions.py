import pandas as pd
from geopy.distance import geodesic
import requests
import us  

API_KEY = 'SVIWSxowXKKfzsXFqkAbVWd8NAmZeDns'

def get_events_by_city(city, state, API_KEY):
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    
    params = {
        "apikey": API_KEY,
        "city": city,
        "classificationName": "music"
    }

    if state:
        params["stateCode"] = state

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        events = data.get("_embedded", {}).get("events", [])
        
        if not events:
            return []

        event_details = []
        for event in events:
            venue = event.get("_embedded", {}).get("venues", [{}])[0]
            venue_city = venue.get("city", {}).get("name", "Unknown City")
            venue_state = venue.get("state", {}).get("stateCode", "Unknown State")
            
            event_name = event["name"]
            event_date = event["dates"]["start"].get("localDate", "TBD")

            event_details.append((event_name, event_date, venue_city, venue_state))
        
        return event_details

    else:
        return []

def handle_ambiguous_city(city, state, API_KEY):
    """
    Handle the case where a city name exists in multiple states.
    
    Args:
        city (str): Name of the city to search for events.
        api_key (str): Ticketmaster API key.
    
    Returns:
        list: A list of events for the specified city or a prompt to select a state.
    """
    events = get_events_by_city(city, state, API_KEY)
    
    if events:
        city_state_pairs = set((event[2], event[3]) for event in events)

        if len(city_state_pairs) > 1:
            for venue_city, venue_state in city_state_pairs:

                state_full_name = us.states.lookup(venue_state).name
                state_abbr = us.states.lookup(venue_state).abbr            
            state_input = input(f"Enter the state for {city} (e.g., IL for Illinois or full name like 'Illinois'): ").strip()

            try:
                state_abbr = us.states.lookup(state_input).abbr

            except KeyError:

                state_abbr = state_input.upper()
            return get_events_by_city(city, state_abbr, API_KEY)
        else:
            return events
    else:
        return []

def get_cities_within_radius(input_city, radius):
    cities_df = pd.read_csv('uscities.csv')
    
    input_city_data = cities_df[cities_df['city'].str.lower() == input_city.lower()]
    if input_city_data.empty:
        raise ValueError(f"City '{input_city}' not found in the dataset.")
    
    input_coords = (input_city_data.iloc[0]['lat'], input_city_data.iloc[0]['lng'])
    
    cities_within_radius = []
    for _, row in cities_df.iterrows():
        city_coords = (row['lat'], row['lng'])
        distance = geodesic(input_coords, city_coords).miles
        if distance <= radius:
            cities_within_radius.append(row['city'])
    
    return cities_within_radius

def get_events_nearby(input_city, input_state, radius, progress_bar=None):

    radius = float(radius)
    try:
        nearby_cities = get_cities_within_radius(input_city, radius)
    except ValueError as e:
        return
        
    all_events = []
    total_cities = len(nearby_cities)
    for index, city in enumerate(nearby_cities):
        events = handle_ambiguous_city(city, input_state, API_KEY)  # Reuse existing logic
        all_events.extend(events)

        if progress_bar:
            progress_bar.progress((index + 1) / total_cities)
   
    return all_events