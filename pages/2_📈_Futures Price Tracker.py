import streamlit as st
import sqlite3
import pandas as pd
import numpy as np

# Compatibility shim for numpy legacy type names (e.g. np.bool8)
try:
    if not hasattr(np, 'bool8'):
        np.bool8 = np.bool_
except Exception:
    pass
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from io import BytesIO
from xlsxwriter import Workbook


st.set_page_config(
    page_title='HUMQuote - Futures Price Tracker', 
    page_icon='📈', 
    initial_sidebar_state="auto",
    layout='wide',
    menu_items={
        'Get Help': 'https://www.humenergy.com.au/',
        'Report a bug': "https://www.humenergy.com.au/contact",
        'About': "# Bulk Electricity Pricing tool for Large Contracts"
    }
)

#########################################################################################################
#########################################################################################################
# FUTURES PRICE TRACKER
#########################################################################################################
#########################################################################################################

st.image("hum-solar-header.jpg", use_container_width=True)

# Streamlit UI for Database Explorer
st.title("📈 Futures Price Tracker")

#st.sidebar.image("logo_hum.png", width='stretch')

#########################################################################################################
#########################################################################################################
# FUNCTIONS
#########################################################################################################
#########################################################################################################

# Function to fetch data from the database, sorted by "Quote Date" in descending order
def fetch_data_from_database(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    # Modify the query to include an ORDER BY clause for "Quote Date" in descending order
    query = "SELECT * FROM futures_data ORDER BY `Quote Date` DESC"
    # Execute the query and fetch the data
    df = pd.read_sql_query(query, conn)
    # Close the database connection
    conn.close()
    return df

# Function to initialize and store the DataFrame in session state
def initialize_data():
    # Check if 'futures_data' is not in session state or you need to refresh it
    if 'futures_data' not in st.session_state:
        # Fetch the data from the database and store it in session state
        st.session_state['futures_data'] = fetch_data_from_database('futures_prices.db')



# Example of using the DataFrame in your Streamlit app
def display_data_table():
    # Access the DataFrame from the session state
    df = st.session_state['futures_data'].set_index('Quote Date')

    # Display the DataFrame in the app
    expander_futures = st.expander(f"# Historical Futures Data", expanded=False)
    with expander_futures:
        st.table(df)

    # Optional: Download button for the data
    csv = df.to_csv(index=True).encode('utf-8')
    st.download_button("Download as CSV", csv, "historical-futures-data.csv", "text/csv", key='download-csv')


# Assuming the DataFrame is already stored in the session state as 'futures_data'
# Make sure this function is called after 'initialize_data()' is called
def display_chart():
    df = st.session_state['futures_data'].copy()

    if df.empty:
        st.warning("No futures data available to plot.")
        return

    if "Quote Date" in df.columns:
        df["Quote Date"] = pd.to_datetime(df["Quote Date"], errors="coerce")

    if "Year" in df.columns:
        df["Year"] = df["Year"].astype(str)

    # Dropdown for selecting the column to plot
    selected_column = st.selectbox("Select State to plot:", ["NSW", "VIC", "QLD", "SA"])

    if selected_column not in df.columns:
        st.error(f"Selected column '{selected_column}' is not present in the futures data.")
        return

    # Draw one manual trace per Year to avoid Plotly Express group-by issues
    fig = go.Figure()
    for year, group in df.groupby('Year'):
        fig.add_trace(go.Scatter(
            x=group['Quote Date'],
            y=group[selected_column],
            mode='lines+markers',
            name=str(year),
            connectgaps=True,
        ))

    fig.update_layout(
        title=f"{selected_column} Futures Prices Over Time",
        xaxis_title="Quote Date",
        yaxis_title="$AUD/MWh",
        height=500,
        legend_title="Year",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display the DataFrame
    #st.write(df)



#########################################################################################################
#########################################################################################################
# WORKFLOW
#########################################################################################################
#########################################################################################################


# Call the function to initialize the data on app start or when needed
initialize_data()

# Ensure to call initialize_data() before this if it's not already done
# Example of using the DataFrame and chart in your Streamlit app
display_chart()

# Assuming this is a multi-page app, you can call display_data on any page
display_data_table()
