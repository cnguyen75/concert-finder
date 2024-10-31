import requests
import json
import csv

sapi_key = 'SVIWSxowXKKfzsXFqkAbVWd8NAmZeDns'
url = 'https://app.ticketmaster.com/discovery/v2/classifications.json'

def fetch_genres():
    params = {
        'apikey': sapi_key,
        'size': 200
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Failed to fetch data. Status Code: {response.status_code}")
        return []
    
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Error decoding JSON response")
        return []
    
    genres = []
    
    # Navigate through nested structure to find genres with both ID and name
    if '_embedded' in data and 'classifications' in data['_embedded']:
        for classification in data['_embedded']['classifications']:
            if 'segment' in classification and '_embedded' in classification['segment']:
                for genre in classification['segment']['_embedded'].get('genres', []):
                    if 'id' in genre and 'name' in genre:
                        genres.append((genre['id'], genre['name']))
                
    return genres

def save_to_csv(genres):
    with open("genres.csv", mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Genre ID", "Genre Name"])
        for genre_id, genre_name in genres:
            writer.writerow([genre_id, genre_name])


if __name__ == "__main__":
    genres = fetch_genres()
    print("Total genres found:", len(genres))
    print("Genres:", genres)
    save_to_csv(genres)
    print("Genres saved to genres.csv")
