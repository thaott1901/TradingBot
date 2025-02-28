import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime, timedelta, timezone
from config import API_KEY, SECRET_KEY, BASE_URL, SYMBOL, TIMEFRAME

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")

def get_stock_data(symbol=SYMBOL, timeframe=TIMEFRAME, limit=100):
    """Fetch historical stock data."""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=limit)  # Fetch last xx days of data

    # Convert to RFC 3339 format (YYYY-MM-DDTHH:MM:SSZ)
    start_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")  # No microseconds
    end_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")  # No microseconds

    try:
        # Fetch bars with corrected time format
        bars = api.get_bars(symbol, timeframe, start=start_str, end=end_str, limit=limit, feed="iex")

        # Debugging: Print raw response
        # print(f"API response: {bars}")

        # Check if bars are returned
        if bars:
            print(f"Fetched {len(bars)} bars for {symbol}")
            df = bars.df  # Convert to DataFrame
            df = df.sort_index()  # Ensure data is sorted by time
            return df
        else:
            print(f"No data returned for {symbol}")
            return pd.DataFrame()  # Return an empty DataFrame if no data

    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return pd.DataFrame()


# Test fetching data
if __name__ == "__main__":
    data = get_stock_data()
    print(data.tail())  # Show last few rows
