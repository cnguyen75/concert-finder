import streamlit as st
import pandas as pd
from functions import *
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

CITIES_FILE = "uscities.csv"
cities_df = pd.read_csv(CITIES_FILE)

if "selected_event_id" not in st.session_state:
    st.session_state.selected_event_id = None
if "events_df" not in st.session_state:
    st.session_state.events_df = pd.DataFrame()

st.title("Event Finder")
st.text("Welcome to our event finder! Please fill out the search criteria to the left, and we will find Ticketmaster events for you!")
st.sidebar.header("Search Criteria")

state = st.sidebar.selectbox(
    "Select a State:", 
    cities_df['state_name'].unique(), 
    key="state_select"
)
city = st.sidebar.selectbox(
    "Select a City:", 
    cities_df[cities_df['state_name'] == state]['city'].unique(), 
    key="city_select"
)
radius = st.sidebar.slider(
    "How far are you willing to travel (in miles)?", 
    min_value=10, 
    max_value=100, 
    step=10, 
    value=20, 
    key="radius_slider"
)
if st.sidebar.button("Find Events"):
    st.session_state.selected_event_id = None  # Reset the selection
    st.write(f"Finding events within {radius} miles of **{city}**...")

    progress_bar = st.progress(0)
    state_id = cities_df[cities_df['state_name'] == state]['state_id'].iloc[0]
    events = get_events_nearby(city, state_id, radius, progress_bar)
    progress_bar.empty()

    if events:
        st.success(f"Found {len(events)} events!")

        events_df = pd.DataFrame(events, columns=["Event", "Date", "City", "State", "Event ID"])
        events_df['datetime'] = pd.to_datetime(events_df['Date'])
        sorted_events_df = events_df.sort_values(by='datetime', ascending=True).reset_index(drop=True)

        st.session_state.events_df = sorted_events_df 
    else:
        st.warning("It doesn't seem like there are any events in the specified area. Better luck next time!")
        st.session_state.events_df = pd.DataFrame() 

if not st.session_state.events_df.empty:
    st.write("### Select an Event from the Table Below")
    
    grid_options = GridOptionsBuilder.from_dataframe(st.session_state.events_df[["Event", "Date", "City", "State",  "Event ID"]])
    grid_options.configure_selection("single")  
    grid_options = grid_options.build()

    grid_response = AgGrid(
        st.session_state.events_df[["Event", "Date", "City", "State", "Event ID"]],
        gridOptions=grid_options,
        height=300,
        theme="streamlit",
        update_mode="MODEL_CHANGED",
        allow_unsafe_jscode=True,
    )

    selected_row = grid_response.get("selected_rows", [])  

    if selected_row is not None:  
        if len(selected_row) > 0:
            st.session_state.selected_event_id = selected_row.iloc[0]["Event ID"] 
            st.session_state.show_event_details = True
        else:
            st.session_state.selected_event_data = None
            st.session_state.show_event_details = False
    else:
        st.session_state.selected_event_data = None
        st.session_state.show_event_details = False

if st.session_state.selected_event_id:
    event_details = get_event_details(st.session_state.selected_event_id)

    st.write("## Event Details")
    st.write(f"**Event:** {event_details.get('event_name', 'N/A')}")
    st.write(f"**Date:** {event_details.get('date', 'N/A')}")
    st.write(f"**City:** {event_details.get('city', 'N/A')}")
    st.write(f"**State:** {event_details.get('state', 'N/A')}")
    st.write(f"**Description:** {event_details.get('description', 'N/A')}")
    st.write(f"**Venue:** {event_details.get('venue', 'N/A')}")

    st.write("### Sales Information")
    st.write(f"**Public Sale Start:** {event_details['sales'].get('public_start', 'N/A')}")
    st.write(f"**Public Sale End:** {event_details['sales'].get('public_end', 'N/A')}")

    st.write("### Price Ranges")
    if event_details["price_ranges"]:
        for price_range in event_details["price_ranges"]:
            min_price = f"\\${price_range['min_price']:,}"  
            max_price = f"\\${price_range['max_price']:,}"  
            currency = price_range["currency"]
            st.markdown(
                f"- **Min Price:** {min_price} | "
                f"**Max Price:** {max_price} | "
                f"**Currency:** {currency}"
            )
    else:
        st.write("Price range information is not available.")
        
    st.write(f"**Ticket Link:** [Buy Tickets Here]({event_details.get('ticket_link', '#')})")

