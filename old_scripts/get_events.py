import requests
import csv
import json

api_key = 'SVIWSxowXKKfzsXFqkAbVWd8NAmZeDns'
event_url = 'https://app.ticketmaster.com/discovery/v2/events.json'

def load_genres():
    genres = {}
    with open("genres.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            genres[row["Genre Name"]] = row["Genre ID"]
    return genres

def get_user_preferences():
    # Get user input for ZIP code and driving distance
    zip_code = input("Enter your ZIP code: ")
    radius = input("How far are you willing to drive (in miles)? ")
    return zip_code, radius

def fetch_events_by_zip_and_radius(zip_code, radius): 
    #For some reason, won't fetch unless it's the direct zipcode of a venue
    params = {
        'apikey': api_key,
        'postalCode': zip_code,
        'radius': radius,
        'unit': 'miles',      
        'size': 100,           
        'sort': 'date,asc'    
    }

    response = requests.get(event_url, params=params)
    print("Request URL:", response.url)  # Print URL for debugging

    if response.status_code != 200:
        print(f"Failed to fetch data. Status Code: {response.status_code}")
        print("Response content:", response.text)
        return []

    data = response.json()
    events = data.get('_embedded', {}).get('events', [])
    return events

def display_events(events):
    if not events:
        print("No events found.")
        return

    print("\nEvents found:")
    for event in events:
        name = event.get('name', 'N/A')
        date = event.get('dates', {}).get('start', {}).get('localDate', 'N/A')
        venue_info = event.get('_embedded', {}).get('venues', [{}])[0]
        venue = venue_info.get('name', 'N/A')
        city = venue_info.get('city', {}).get('name', 'N/A')
        
        # Extract genre information
        classifications = event.get('classifications', [])
        genre = classifications[0].get('genre', {}).get('name', 'N/A') if classifications else 'N/A'
        
        print(f"Event: {name} | Date: {date} | Venue: {venue} | City: {city} | Genre: {genre}")

if __name__ == "__main__":
    # Get user preferences
    zip_code, radius = get_user_preferences()

    # Fetch and display events based on user input
    events = fetch_events_by_zip_and_radius(zip_code, radius)
    display_events(events)







