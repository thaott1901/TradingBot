# Moving average crossover
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np  # ✅ Import NumPy

def plot_strategy(data):
    """Plot stock price, moving averages, Bollinger Bands, and RSI only if they exist."""
    # ✅ Debugging: Check type before plotting
    print("Before plotting, data type:", type(data))

    # ✅ Fix: If data is a NumPy array, convert it back to DataFrame
    if isinstance(data, np.ndarray):
        raise ValueError("Error: Data was converted to NumPy array. Expected Pandas DataFrame.")

    if not isinstance(data, pd.DataFrame):
        raise ValueError(f"Error: Expected Pandas DataFrame, but got {type(data)} instead.")

    # ✅ Debug: Ensure 'close' column exists
    if "close" not in data.columns:
        raise ValueError("Error: 'close' column is missing from DataFrame.")
    
    # Check if RSI is available
    has_rsi = "rsi" in data.columns

    # Create one or two subplots based on whether RSI is present
    # fig, ax1 = plt.subplots(figsize=(10, 6)) if not has_rsi else plt.subplots(2, figsize=(10, 8), sharex=True)
    # ✅ Correctly assign subplots
    if has_rsi:
        fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 8), sharex=True)  # Two subplots
    else:
        fig, ax1 = plt.subplots(figsize=(10, 6))  # Single subplot
        ax2 = None  # No RSI plot needed

    # --- Upper Plot: Price & Indicators ---
    ax1.plot(data.index, data["close"], label="Close Price", color="black", linewidth=1)

    # Plot Moving Averages if available
    if "short_ma" in data.columns and "long_ma" in data.columns:
        ax1.plot(data.index, data["short_ma"], label="Short MA (10)", color="blue", linestyle="--")
        ax1.plot(data.index, data["long_ma"], label="Long MA (50)", color="red", linestyle="--")

    # Plot Bollinger Bands if available
    if "upper_band" in data.columns and "lower_band" in data.columns:
        ax1.plot(data.index, data["upper_band"], label="Upper Bollinger Band", color="green", linestyle="--")
        ax1.plot(data.index, data["lower_band"], label="Lower Bollinger Band", color="green", linestyle="--")

    # Buy signals (green arrow)
    buy_signals = data[data["signal"] == 1]
    ax1.scatter(buy_signals.index, buy_signals["close"], marker="^", color="green", label="Buy Signal", alpha=1)

    # Sell signals (red arrow)
    sell_signals = data[data["signal"] == -1]
    ax1.scatter(sell_signals.index, sell_signals["close"], marker="v", color="red", label="Sell Signal", alpha=1)

    ax1.set_title("Trading Strategy Visualization")
    ax1.set_ylabel("Price")
    ax1.legend()
    ax1.grid()

    # --- Lower Plot: RSI (Only If Available) ---
    if has_rsi:
        ax2 = fig.add_subplot(212, sharex=ax1)  # Add RSI subplot
        ax2.plot(data.index, data["rsi"], label="RSI", color="purple")
        ax2.axhline(70, linestyle="--", color="red", alpha=0.7, label="Overbought (70)")
        ax2.axhline(30, linestyle="--", color="green", alpha=0.7, label="Oversold (30)")

        ax2.set_title("Relative Strength Index (RSI)")
        ax2.set_ylabel("RSI Value")
        ax2.legend()
        ax2.grid()

    # Format the x-axis date labels
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    fig.autofmt_xdate()

    plt.show()

