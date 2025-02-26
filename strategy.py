import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def moving_average_strategy(data, short_window=10, long_window=50):
    """Generate buy/sell signals based on Moving Average Crossover."""
    data = data.copy()  # Avoid modifying original DataFrame

    # Calculate moving averages
    data["short_ma"] = data["close"].rolling(window=short_window).mean()
    data["long_ma"] = data["close"].rolling(window=long_window).mean()

    # Generate signals
    data["signal"] = 0  # Default: No position
    data.loc[data["short_ma"] > data["long_ma"], "signal"] = 1  # Buy
    data.loc[data["short_ma"] < data["long_ma"], "signal"] = -1  # Sell

    return data

def plot_strategy(data):
    """Plot the stock price and moving averages."""
    plt.figure(figsize=(10, 6))

    # Plot the close price
    plt.plot(data.index, data["close"], label="Close Price", color="black", linewidth=1)

    # Plot short and long moving averages
    plt.plot(data.index, data["short_ma"], label="Short Moving Average (10)", color="blue", linestyle="--")
    plt.plot(data.index, data["long_ma"], label="Long Moving Average (50)", color="red", linestyle="--")

    # Plot buy signals (green arrow)
    buy_signals = data[data["signal"] == 1]
    plt.scatter(buy_signals.index, buy_signals["close"], marker="^", color="green", label="Buy Signal", alpha=1)

    # Plot sell signals (red arrow)
    sell_signals = data[data["signal"] == -1]
    plt.scatter(sell_signals.index, sell_signals["close"], marker="v", color="red", label="Sell Signal", alpha=1)

    # Format the plot
    plt.title("Moving Average Crossover Strategy")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    
    # Improve date formatting on the x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.gcf().autofmt_xdate()

    # Show the plot
    plt.show()

# Test the strategy and plot
if __name__ == "__main__":
    from data_handler import get_stock_data
    
    stock_data = get_stock_data(symbol="TSLA", limit=100)  # Fetch 100 bars
    strategy_data = moving_average_strategy(stock_data)

    # Save the dataframe to a CSV file
    strategy_data.to_csv('strategy_output.csv')


    # Plot the strategy
    plot_strategy(strategy_data)
