README.txt
Stock Analytics Dashboard

A full desktop app I built that lets you look up any stock and see
6 months of price history with moving averages charted right inside
the window. It also flags unusual trading days using machine learning
and saves every search to a local database so you can look back at
your history later.

This is the most complete project in my portfolio so far. It combines
the analytics module I built earlier with a full GUI, a live chart,
and a database all in one app.

Language: Python
Libraries: yfinance (pulls live stock data from Yahoo Finance),
           pandas and numpy (data cleaning and calculations),
           matplotlib (draws the price chart inside the window),
           scikit-learn / IsolationForest (detects unusual price days),
           sqlite3 (saves and retrieves search history locally),
           Tkinter and matplotlib FigureCanvasTkAgg (GUI and chart embedding)

Notes:
- Install libraries first: pip install yfinance pandas numpy matplotlib scikit-learn
- sqlite3 comes built into Python, no install needed.
- A file called stock_history.db will be created automatically on first run.
- The chart shows Close Price, SMA 30, SMA 60, EMA 20, and anomaly dots.
- Press Enter or click Analyze after typing a ticker symbol.
- Use View History to see all past searches, Clear History to wipe them.
