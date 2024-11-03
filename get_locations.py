import requests
import json
import csv
import time

api_key = 'SVIWSxowXKKfzsXFqkAbVWd8NAmZeDns'
event_url = 'https://app.ticketmaster.com/discovery/v2/events.json'
venue_url = 'https://app.ticketmaster.com/discovery/v2/venues/'

def fetch_music_event_venues():
    page_number = 0
    unique_venues = {}
    params = {
        'apikey': api_key,
        'classificationName': 'music',
        'size': 200,
    }
    
    while True:
        params['page'] = page_number
        response = requests.get(event_url, params=params)
        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status Code: {response.status_code}")
            break
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error decoding JSON response")
            break
        
        # Check if there are any events in the response
        if 'events' not in data.get('_embedded', {}):
            break
        
        # Collect unique venues
        for event in data['_embedded']['events']:
            for venue in event['_embedded'].get('venues', []):
                venue_id = venue.get('id')
                if venue_id and venue_id not in unique_venues:
                    unique_venues[venue_id] = {
                        'name': venue.get('name', 'N/A'),
                        'address': venue.get('address', {}).get('line1', 'N/A'),
                        'city': venue.get('city', {}).get('name', 'N/A'),
                        'state': venue.get('state', {}).get('name', 'N/A'),
                        'country': venue.get('country', {}).get('name', 'N/A')
                    }
        
        # Check if there are more pages
        page_number += 1
        if page_number >= data['page']['totalPages']:
            break
        
        # Respect API rate limits
        time.sleep(0.2)

    return unique_venues

def save_venues_to_csv(venues):
    with open("venues.csv", mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Venue ID", "Venue Name", "Address", "City", "State", "Country"])
        for venue_id, venue_info in venues.items():
            writer.writerow([venue_id, venue_info['name'], venue_info['address'], venue_info['city'], venue_info['state'], venue_info['country']])

if __name__ == "__main__":
    venues = fetch_music_event_venues()
    print("Total unique venues found:", len(venues))
    save_venues_to_csv(venues)
    print("Venue locations saved to venues.csv")