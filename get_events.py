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
    params = {
        'apikey': api_key,
        'postalCode': zip_code,
        'radius': radius,
        'unit': 'miles',      # You can switch to 'km' if preferred
        'size': 10,           # Limit the number of results per page for testing
        'sort': 'date,asc'    # Optional: Sort results by date in ascending order
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
        venue = event.get('_embedded', {}).get('venues', [{}])[0].get('name', 'N/A')
        print(f"Event: {name} | Date: {date} | Venue: {venue}")

if __name__ == "__main__":
    # Get user preferences
    zip_code, radius = get_user_preferences()

    # Fetch and display events based on user input
    events = fetch_events_by_zip_and_radius(zip_code, radius)
    display_events(events)







