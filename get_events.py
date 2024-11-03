import requests
import csv
import time
import json

api_key = 'SVIWSxowXKKfzsXFqkAbVWd8NAmZeDns'
event_url = 'https://app.ticketmaster.com/discovery/v2/events.json'

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
        
        # Print the full URL to debug parameter issues
        print("Requesting URL:", response.url)
        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status Code: {response.status_code}")
            print("Response content:", response.text)
            break
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error decoding JSON response")
            break
        
        # Check if there are any events in the response
        if 'events' not in data.get('_embedded', {}):
            break
        
        # Collect unique venues, only if they are in the United States
        for event in data['_embedded']['events']:
            artist = event.get('name', 'N/A')  # The event name often includes the artist
            event_date = event.get('dates', {}).get('start', {}).get('localDate', 'N/A')
            
            for venue in event['_embedded'].get('venues', []):
                venue_id = venue.get('id')
                country = venue.get('country', {}).get('name', 'N/A')
                
                # Normalize the country name for comparison
                if venue_id and country.lower().strip() == "united states of america".lower().strip() and venue_id not in unique_venues:
                    unique_venues[venue_id] = {
                        'name': venue.get('name', 'N/A'),
                        'address': venue.get('address', {}).get('line1', 'N/A'),
                        'city': venue.get('city', {}).get('name', 'N/A'),
                        'state': venue.get('state', {}).get('name', 'N/A'),
                        'country': country,
                        'artist': artist,
                        'date': event_date
                    }
                else:
                    # Print out the country for debugging purposes
                    print(f"Skipping venue with country: {country}")
        
        # Check if there are more pages
        page_number += 1
        if page_number >= data['page']['totalPages']:
            break
        
        # Respect API rate limits
        time.sleep(0.2)

    return unique_venues

def save_events_to_csv(venues):
    with open("events.csv", mode="w", newline='') as file:  # Change filename to "events.csv"
        writer = csv.writer(file)
        writer.writerow(["Venue ID", "Venue Name", "Address", "City", "State", "Country", "Artist", "Date"])
        for venue_id, venue_info in venues.items():
            writer.writerow([
                venue_id, venue_info['name'], venue_info['address'], venue_info['city'], 
                venue_info['state'], venue_info['country'], venue_info['artist'], venue_info['date']
            ])

if __name__ == "__main__":
    venues = fetch_music_event_venues()
    print("Total unique venues found:", len(venues))
    save_events_to_csv(venues)  # Updated to save in events.csv
    print("Event details saved to events.csv")







