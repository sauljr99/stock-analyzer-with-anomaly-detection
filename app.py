import streamlit as st          # Streamlit is the web framework that builds the browser UI
import matplotlib.pyplot as plt  # Matplotlib draws the stock price chart
import sqlite3                   # SQLite lets us read/write the local database file
import sys                       # sys lets us modify Python's module import system
import unittest.mock as mock     # mock lets us fake tkinter so the import doesn't crash

# ── TKINTER SUPPRESSION ───────────────────────────────────────────────────────
# Your original file imports tkinter, which is a desktop GUI library.
# Streamlit runs in a browser, so tkinter can't open windows here.
# Instead of removing those imports from your original file, we trick Python
# into thinking tkinter is already loaded by replacing it with a fake (mock) object.
# This way your original file imports without crashing.
sys.modules['tkinter'] = mock.MagicMock()
sys.modules['tkinter.messagebox'] = mock.MagicMock()
sys.modules['matplotlib.backends.backend_tkagg'] = mock.MagicMock()

# ── IMPORT FROM YOUR ORIGINAL FILE ───────────────────────────────────────────
# We pull the three backend functions directly from your original file.
# run_analysis()    → downloads stock data, calculates moving averages, detects anomalies
# create_database() → creates stock_history.db if it doesn't already exist
# save_to_history() → inserts a new row into the database after each search
# Your original file is never modified — we just borrow these functions.
from Milestone_3_BUS472 import run_analysis, create_database, save_to_history

# ── DATABASE HELPER: READ HISTORY ────────────────────────────────────────────
def get_history():
    # Open a connection to the local SQLite database file
    conn = sqlite3.connect("stock_history.db")
    cursor = conn.cursor()
    # Fetch all past searches, newest first (ORDER BY id DESC)
    cursor.execute("""
        SELECT ticker, latest_price, avg_price, high_price, low_price, trend, total_return, search_date
        FROM search_history
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()  # Store all rows as a list of tuples
    conn.close()              # Always close the connection when done
    return rows               # Return the list so it can be displayed in the UI

# ── DATABASE HELPER: CLEAR HISTORY ───────────────────────────────────────────
def clear_history_db():
    # Open the database and delete every row from the search history table
    conn = sqlite3.connect("stock_history.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search_history")  # Wipes all rows permanently
    conn.commit()   # Save the deletion to disk
    conn.close()    # Close the connection

# ── APP INITIALIZATION ────────────────────────────────────────────────────────
# Call create_database() once when the app starts so the table exists
# before any searches are made or history is read
create_database()

# Set the browser tab title and use wide layout so the chart has more space
st.set_page_config(page_title="Stock Analytics Dashboard", layout="wide")

# Display the main title at the top of the page
st.title("📈 Stock Analytics Dashboard")

# ── INPUT ROW ─────────────────────────────────────────────────────────────────
# Split the top of the page into 4 columns: text box, and 3 buttons
# [2, 1, 1, 1] means the text box gets twice as much space as each button
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    # Text box where the user types a ticker symbol (e.g. AAPL)
    # .strip() removes accidental spaces, .upper() makes it uppercase
    ticker_input = st.text_input("Enter a ticker symbol:", placeholder="e.g. AAPL").strip().upper()
with col2:
    # Analyze button — when clicked, analyze_btn becomes True
    analyze_btn = st.button("Analyze", use_container_width=True)
with col3:
    # View History button — when clicked, view_history_btn becomes True
    view_history_btn = st.button("View History", use_container_width=True)
with col4:
    # Clear History button — when clicked, clear_history_btn becomes True
    clear_history_btn = st.button("Clear History", use_container_width=True)

# ── CLEAR HISTORY LOGIC ───────────────────────────────────────────────────────
if clear_history_btn:
    clear_history_db()                      # Delete all rows from the database
    st.success("Search history cleared.")   # Show a green confirmation message

# ── VIEW HISTORY LOGIC ────────────────────────────────────────────────────────
if view_history_btn:
    rows = get_history()          # Pull all past searches from the database
    st.subheader("Past Searches") # Display a section heading
    if not rows:
        # If no searches have been saved yet, show an info message
        st.info("No search history yet.")
    else:
        import pandas as pd
        # Convert the list of tuples into a DataFrame so it displays as a table
        df_hist = pd.DataFrame(rows, columns=[
            "Ticker", "Latest Price", "Avg Price", "High Price",
            "Low Price", "Trend", "Total Return (%)", "Search Date"
        ])
        # Render the DataFrame as an interactive table that fills the page width
        st.dataframe(df_hist, use_container_width=True)

# ── ANALYZE LOGIC ─────────────────────────────────────────────────────────────
if analyze_btn:
    if not ticker_input:
        # If the user clicked Analyze without typing anything, show a warning
        st.warning("Please enter a stock ticker symbol.")
    else:
        # Show a spinning loading message while data is being fetched
        with st.spinner(f"Fetching data for {ticker_input}..."):
            try:
                # Call your original run_analysis() function with the ticker
                # Returns: df (price data), stats (key numbers), anomalies (unusual days)
                df, stats, anomalies = run_analysis(ticker_input)

                # Save this search result to the database using your original function
                save_to_history(stats)

                # Split the results area into two columns: stats on left, chart on right
                # [1, 3] means the chart gets 3x more space than the stats panel
                left, right = st.columns([1, 3])

                with left:
                    st.subheader("Summary")
                    # Display each key stat as its own metric card (label on top, value below)
                    st.metric("Latest Price",  f"${stats['latest']}")
                    st.metric("6-Mo Average",  f"${stats['avg']}")
                    st.metric("6-Mo High",     f"${stats['high']}")
                    st.metric("6-Mo Low",      f"${stats['low']}")
                    st.metric("SMA 30",        f"${stats['sma_30']}")
                    st.metric("SMA 60",        f"${stats['sma_60']}")
                    st.metric("EMA 20",        f"${stats['ema_20']}")
                    st.metric("Trend",         stats['trend'])
                    st.metric("Daily Return",  f"{stats['daily_return']}%")
                    st.metric("Total Return",  f"{stats['total_return']}%")
                    st.metric("Anomalies",     f"{len(anomalies)} unusual day(s)")

                with right:
                    st.subheader(f"{stats['ticker']} — Last 6 Months")
                    # Create a matplotlib figure (same chart logic as your original file)
                    fig, ax = plt.subplots(figsize=(10, 4.5))
                    # Plot closing price as a solid blue line
                    ax.plot(df.index, df['Close'],  label='Close Price', color='steelblue', linewidth=1.5)
                    # Plot the three moving averages as dashed lines
                    ax.plot(df.index, df['SMA_30'], label='SMA 30',      color='orange',   linewidth=1, linestyle='--')
                    ax.plot(df.index, df['SMA_60'], label='SMA 60',      color='green',    linewidth=1, linestyle='--')
                    ax.plot(df.index, df['EMA_20'], label='EMA 20',      color='purple',   linewidth=1, linestyle='--')
                    # If any anomaly days were detected, plot them as red dots
                    if not anomalies.empty:
                        ax.scatter(anomalies.index, anomalies['Close'],
                                   color='red', zorder=5, label='Anomaly', s=40)
                    ax.set_xlabel("Date")           # Label the x-axis
                    ax.set_ylabel("Price (USD)")    # Label the y-axis
                    ax.legend(loc='upper left', fontsize=7)  # Show the legend
                    ax.tick_params(axis='x', rotation=45)    # Rotate dates so they don't overlap
                    plt.tight_layout()              # Auto-adjust spacing so nothing gets cut off
                    st.pyplot(fig)                  # Render the chart inside the Streamlit page

            except Exception as e:
                # If anything goes wrong (bad ticker, no internet, etc.), show a red error message
                st.error(f"Could not fetch data: {e}")