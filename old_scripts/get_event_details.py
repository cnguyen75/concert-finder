import requests

api_key = 'SVIWSxowXKKfzsXFqkAbVWd8NAmZeDns'
event_url = 'https://app.ticketmaster.com/discovery/v2/events.json'

def get_event_details(event_name, city, state):
    """
    Fetch detailed information about a specific event.

    Args:
        event_name (str): The name of the event.
        city (str): The city where the event is located.
        state (str): The state where the event is located.

    Returns:
        dict: A dictionary containing detailed event information.
    """
    # Example API call to get event details
    # Replace this with your actual API endpoint and parameters
    params = {
        "event_name": event_name,
        "city": city,
        "state": state,
        "apikey": api_key  
    }
    response = requests.get(event_url, params=params)
    
    if response.status_code == 200:
        return response.json()  # Adjust to fit your API's response structure
    else:
        return {"error": f"Unable to fetch event details: {response.status_code}"}
