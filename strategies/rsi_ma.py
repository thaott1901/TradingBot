import pandas as pd
import ta
import sys
import os

# Add the parent directory to sys.path so Python can find `data_handler.py`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_handler import get_stock_data  
from strategies.strategy import plot_strategy  

def rsi_ma_strategy(data, short_window=10, long_window=50, rsi_period=14):
    """Generate buy/sell signals using RSI + Moving Average Crossover."""
    data = data.copy()

    # ✅ Debug: Print before processing
    print("Before RSI processing:", type(data))

    # Calculate moving averages
    data["short_ma"] = data["close"].rolling(window=short_window).mean()
    data["long_ma"] = data["close"].rolling(window=long_window).mean()

    data["short_ma"] = data["short_ma"].bfill()
    data["long_ma"] = data["long_ma"].bfill()

    # Calculate RSI
    data["rsi"] = ta.momentum.RSIIndicator(data["close"], window=rsi_period).rsi()

    # Generate signals
    data["signal"] = 0
    for i in range(len(data)):
        if i == 0:
            continue  # Skip first row

        short_ma = data["short_ma"].iloc[i]
        long_ma = data["long_ma"].iloc[i]
        rsi = data["rsi"].iloc[i]

        print(f"🔍 Checking {data.index[i]}: short_ma={short_ma:.2f}, long_ma={long_ma:.2f}, RSI={rsi:.2f}")

        if short_ma > long_ma and rsi < 40:
            print(f"✅ BUY SIGNAL TRIGGERED on {data.index[i]}")
            data.at[data.index[i], "signal"] = 1  # Buy signal

        elif short_ma < long_ma and rsi > 60:
            print(f"❌ SELL SIGNAL TRIGGERED on {data.index[i]}")
            data.at[data.index[i], "signal"] = -1  # Sell signal


    # ✅ Debug: Print after processing
    print("After RSI processing:", type(data))
    print("Before returning:")
    print(data.dtypes)  # Check data types
    print(data.head())  # Check if RSI exists
    # Debugging
    print("Final data type before returning:", type(data))  # Should be <class 'pandas.DataFrame'>
    return data

# Test the strategy
if __name__ == "__main__":
    stock_data = get_stock_data(symbol="NVDA", limit=100)
    print(stock_data.head())  # ✅ Debugging: Check DataFrame columns

    strategy_data = rsi_ma_strategy(stock_data)

    # Save the output
    strategy_data.to_csv("rsi_ma_output.csv")

    # Plot results
    plot_strategy(strategy_data)
