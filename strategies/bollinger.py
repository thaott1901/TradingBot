import pandas as pd
import ta
import sys
import os

# Add the parent directory to sys.path so Python can find `data_handler.py`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_handler import get_stock_data  
from strategies.strategy import plot_strategy  

def bollinger_strategy(data, window=20, std_dev=2):
    """Generate buy/sell signals using Bollinger Bands."""
    data = data.copy()

    # Calculate Bollinger Bands
    data["middle_band"] = data["close"].rolling(window=window).mean()
    data["std_dev"] = data["close"].rolling(window=window).std()
    data["upper_band"] = data["middle_band"] + (std_dev * data["std_dev"])
    data["lower_band"] = data["middle_band"] - (std_dev * data["std_dev"])

    # Generate buy/sell signals
    data["signal"] = 0
    for i in range(len(data)):
        if i == 0:
            continue  # Skip first row

        if data["close"].iloc[i] > data["upper_band"].iloc[i]:  
            data.at[data.index[i], "signal"] = 1  # Buy Signal
        elif data["close"].iloc[i] < data["lower_band"].iloc[i]:  
            data.at[data.index[i], "signal"] = -1  # Sell Signal

    return data

# Test the strategy
if __name__ == "__main__":
    stock_data = get_stock_data(symbol="TSLA", limit=100)
    strategy_data = bollinger_strategy(stock_data)

    # Save the output
    strategy_data.to_csv("bollinger_output.csv")

    # Plot results
    plot_strategy(strategy_data)
