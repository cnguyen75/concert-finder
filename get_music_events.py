# get_music_events.py

import requests
import csv
import us  # Import the 'us' library

def get_events_by_city(city, state, api_key):
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    
    params = {
        "apikey": api_key,
        "city": city,
        "classificationName": "music"  # Filter for music events
    }

    if state:  # If state is provided, include it in the query
        params["stateCode"] = state

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        events = data.get("_embedded", {}).get("events", [])
        
        if not events:
            print(f"No events found in {city}. Please check the city name or try again.")
            return []

        event_details = []
        for event in events:
            venue = event.get("_embedded", {}).get("venues", [{}])[0]
            venue_city = venue.get("city", {}).get("name", "Unknown City")
            venue_state = venue.get("state", {}).get("stateCode", "Unknown State")
            
            event_name = event["name"]
            event_date = event["dates"]["start"].get("localDate", "TBD")
            
            # Append event details
            event_details.append((event_name, event_date, venue_city, venue_state))
        
        return event_details

    else:
        print(f"Error {response.status_code}: Unable to fetch events.")
        return []

def handle_ambiguous_city(city, api_key):
    """
    Handle the case where a city name exists in multiple states.
    
    Args:
        city (str): Name of the city to search for events.
        api_key (str): Ticketmaster API key.
    
    Returns:
        list: A list of events for the specified city or a prompt to select a state.
    """
    # Try to fetch events for the city without a state specified
    events = get_events_by_city(city, None, api_key)
    
    if events:
        # Check if multiple cities with the same name exist (based on city-state pairs)
        city_state_pairs = set((event[2], event[3]) for event in events)  # (City, State)
        
        if len(city_state_pairs) > 1:
            print(f"Multiple cities with the name '{city}' found. Please specify a state.")
            print("Possible options:")
            for venue_city, venue_state in city_state_pairs:
                # Format as 'city, full state name (abbreviation)'
                state_full_name = us.states.lookup(venue_state).name
                state_abbr = us.states.lookup(venue_state).abbr
                print(f"- {venue_city}, {state_full_name} ({state_abbr})")
            
            state_input = input(f"Enter the state for {city} (e.g., IL for Illinois or full name like 'Illinois'): ").strip()
            
            # Try to handle both full name and abbreviation input
            try:
                # If the user entered a full name, we convert it to the abbreviation
                state_abbr = us.states.lookup(state_input).abbr
            except KeyError:
                # If it’s an abbreviation, the lookup will directly return the abbreviation
                state_abbr = state_input.upper()
            
            return get_events_by_city(city, state_abbr, api_key)
        else:
            # If only one city-state pair, proceed with that result
            return events
    else:
        print(f"No events found for the city '{city}'.")
        return []

def save_events_to_csv(events, city, filename_prefix="events"):
    """
    Save a list of events to a CSV file, using city and state for the filename.
    
    Args:
        events (list): A list of tuples containing event names, dates, city, and state.
        city (str): The city for the events.
        filename_prefix (str): Optional prefix for the filename.
    """
    if events:
        venue_state = events[0][3]
        venue_city = events[0][2]
        
        city_clean = venue_city.replace(" ", "_").replace(",", "").lower()
        state_clean = venue_state.replace(" ", "_").replace(",", "").lower()

        filename = f"{filename_prefix}_{city_clean}_{state_clean}.csv"
        
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Event Name", "Event Date", "City", "State"])  # Header row
            writer.writerows(events)
        
        print(f"Results saved to {filename}")
    else:
        print("No events to save.")

# Example usage
if __name__ == "__main__":
    api_key = "SVIWSxowXKKfzsXFqkAbVWd8NAmZeDns"
    city = input("Enter the city for events: ")
    
    events = handle_ambiguous_city(city, api_key)
    
    if events:
        print(f"Upcoming events in {city}:")
        for event in events:
            print(f"Event: {event[0]}, Date: {event[1]}, City: {event[2]}, State: {event[3]}")
        
        save_events_to_csv(events, city)
    else:
        print("No events to save.")