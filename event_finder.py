import streamlit as st
import pandas as pd
from geopy.distance import geodesic
from functions import *

CITIES_FILE = "uscities.csv"
cities_df = pd.read_csv(CITIES_FILE)

st.title("Event Finder")
st.text("Welcome to our event finder! Please fill out the search criteria to the left and we will find some Ticketmaster events for you to attend!")
st.sidebar.header("Search Criteria")
state = st.sidebar.selectbox("Select a State:", cities_df['state_name'].unique())
city = st.sidebar.selectbox("Select a City:", cities_df[cities_df['state_name'] == state]['city'].unique())
radius = st.sidebar.slider("How far are you willing travel (in miles)?", min_value=10, max_value=100, step=10, value=20)

if st.sidebar.button("Find Events"):
    st.write(f"Finding events within {radius} miles of **{city}**...")
    
    progress_bar = st.progress(0)
    state_id = cities_df[cities_df['state_name'] == state]['state_id'].iloc[0]
    events = get_events_nearby(city, state_id, radius, progress_bar)
    progress_bar.empty()

    if events:
        st.success(f"Found {len(events)} events!")
        events_df = pd.DataFrame(events, columns=["Event", "Date", "City", "State"])

        events_df['datetime'] = pd.to_datetime(events_df['Date'])
        sorted_events_df = events_df.sort_values(by='datetime', ascending=True)
        sorted_events_df = sorted_events_df.drop(columns=['datetime']).reset_index(drop=True)
        st.dataframe(sorted_events_df)
        
    else:
        st.warning("It doesn't seem like there are any events in the specifed area. Better luck next time!")


