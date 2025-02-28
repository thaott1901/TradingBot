import pandas as pd
import sys
import os

# Add the parent directory to sys.path so Python can find `data_handler.py`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_handler import get_stock_data  
from strategies.strategy import plot_strategy  

def moving_average_strategy(data, short_window=10, long_window=50):
    """Generate buy/sell signals based on Moving Average Crossover."""
    data = data.copy()  # Avoid modifying original DataFrame

    # Calculate moving averages
    data["short_ma"] = data["close"].rolling(window=short_window).mean()
    data["long_ma"] = data["close"].rolling(window=long_window).mean()

    # Generate signals
    data["signal"] = 0  # Default: No trade
    data.loc[data["short_ma"] > data["long_ma"], "signal"] = 1  # Buy signal
    data.loc[data["short_ma"] < data["long_ma"], "signal"] = -1  # Sell signal

    # # ✅ Fill NaNs in Moving Averages
    # data["short_ma"].fillna(method="bfill", inplace=True)  
    # data["long_ma"].fillna(method="bfill", inplace=True)

    return data

# Test the strategy
if __name__ == "__main__":

    stock_data = get_stock_data(symbol="TSLA", limit=100)
    strategy_data = moving_average_strategy(stock_data)

    # Save the results
    strategy_data.to_csv("strategy_output.csv")

    # Plot the strategy
    plot_strategy(strategy_data)