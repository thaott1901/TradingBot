import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_handler import get_stock_data
from strategies.moving_average import moving_average_strategy
from strategies.rsi_ma import rsi_ma_strategy
from strategies.bollinger import bollinger_strategy


# Backtest Config
START_CAPITAL = 10000  # Initial capital ($)
TRADE_SIZE = 1  # Shares per trade
STRATEGY = "rsi_ma"  # Choose: "moving_average", "rsi_ma", "bollinger"
TRADE_COMMISSION = 1.00  # $1 per trade
TRAILING_STOP_PERCENT = 0.10  # Sell if price drops 10% from buy price


# Get the strategy function dynamically
strategy_functions = {
    "moving_average": moving_average_strategy,
    "rsi_ma": rsi_ma_strategy,
    "bollinger": bollinger_strategy
}
strategy_function = strategy_functions.get(STRATEGY)

def backtest(data):
    """Run a backtest using historical data."""
    cash = START_CAPITAL  # Initial capital
    position = 0  # Number of shares held
    trade_log = []  # Stores trade history
    current_trade = None  # Store active trade details
    trailing_stop = None  # To store the trailing stop price

    for i in range(len(data)):
        # Buy condition (same as before)
        if data["signal"].iloc[i] == 1 and position == 0:
            buy_price = data["close"].iloc[i]
            num_shares = cash // buy_price
            cost = (num_shares * buy_price) + TRADE_COMMISSION

            if cash >= cost:  # Only buy if enough cash
                cash -= cost
                position += num_shares
                trade_log.append(("BUY", data.index[i], buy_price, num_shares))
                current_trade = {"buy_date": data.index[i], "buy_price": buy_price}
                trailing_stop = buy_price * (1 - TRAILING_STOP_PERCENT)  # Initialize trailing stop
                print(f"✅ EXECUTED BUY: {num_shares} shares at ${buy_price:.2f} on {data.index[i]}")

        # Trailing stop update (if price goes higher, update the stop-loss level)
        if position > 0:
            # If the price goes higher than the current price, adjust the trailing stop
            if data["close"].iloc[i] > current_trade["buy_price"]:
                new_trailing_stop = data["close"].iloc[i] * (1 - TRAILING_STOP_PERCENT)
                if new_trailing_stop > trailing_stop:
                    trailing_stop = new_trailing_stop

        # Ensure trailing_stop is not None before checking
        if trailing_stop is not None:
            # Sell condition (either stop-loss or sell signal)
            if (data["signal"].iloc[i] == -1 or 
                data["close"].iloc[i] <= trailing_stop) and position > 0:
                sell_price = data["close"].iloc[i]
                revenue = position * sell_price
                cash += revenue
                trade_log.append(("SELL", data.index[i], sell_price, position))

                reason = "SELL SIGNAL" if data["signal"].iloc[i] == -1 else f"TRAILING STOP HIT at {trailing_stop:.2f}"
                print(f"❌ {reason}: Sold {position} shares at ${sell_price:.2f} on {data.index[i]} "
                    f"(Profit: ${revenue - (position * current_trade['buy_price']):.2f})")

                position = 0  # Reset position
                current_trade = None  # Reset trade details
                trailing_stop = None  # Reset trailing stop

    # Final portfolio value
    portfolio_value = cash + (position * data["close"].iloc[-1])
    total_return = ((portfolio_value - START_CAPITAL) / START_CAPITAL) * 100

    # Print Summary
    print("\nBacktest Results")
    print(f"Start Capital: ${START_CAPITAL}")
    print(f"End Portfolio Value: ${portfolio_value:.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Total Trades: {len(trade_log) // 2}")  # Divide by 2 since each trade has a buy & sell

    return trade_log, total_return


# Run the backtest
if __name__ == "__main__":

    strategy_function = strategy_functions.get(STRATEGY)
    if strategy_function is None:
        raise ValueError(f"❌ Invalid strategy: {STRATEGY}")

    # 🔹 Define output folder
    OUTPUT_FOLDER = "backtest_results"
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)  # Ensure the folder exists

    # 🔹 Define stock list
    STOCKS = ["AAPL", "MSFT", "NVDA", "META", "AMZN", "TSLA"]  # Add more as needed
    # 🔹 Store results
    results = []

    for stock in STOCKS:
        print(f"\n📈 Running backtest for {stock} using {STRATEGY} strategy...")

        # ✅ Get data
        stock_data = get_stock_data(symbol=stock, limit=365)  

        # Make sure there is sufficient data, otherwise skip this stock
        if len(stock_data) < 50:  
            print(f"⚠️ Not enough data for {stock}. Skipping...")
            continue  # Skip this stock

        strategy_data = strategy_function(stock_data)  # Apply strategy

        print("\n🔍 Checking Signals Before Backtest:")

        # 🔹 Select the correct columns based on strategy
        strategy_columns = {
            "moving_average": ["short_ma", "long_ma", "signal"],
            "rsi_ma": ["short_ma", "long_ma", "rsi", "signal"],
            "bollinger": ["middle_band", "upper_band", "lower_band", "signal"]
        }
        columns_to_print = strategy_columns.get(STRATEGY, ["signal"])

        # 🔹 Safely check if the columns exist before printing
        missing_cols = [col for col in columns_to_print if col not in strategy_data.columns]
        if missing_cols:
            print(f"⚠️ Warning: Missing columns {missing_cols} in {stock}")
        else:
            print(strategy_data[columns_to_print].tail(20))

        # ✅ Debugging: Ensure `strategy_data` is not being modified before passing
        print("\n🔍 Signal Value Counts:")
        print(strategy_data["signal"].value_counts())  

        # ✅ Run backtest
        trade_log, total_return = backtest(strategy_data)

        # ✅ Store results
        results.append({
            "Stock": stock,
            "Total Trades": len(trade_log) // 2,  # Each buy/sell pair is one trade
            "Total Return (%)": round(total_return, 2),
            "Final Portfolio Value": round(START_CAPITAL * (1 + total_return / 100), 2)
        })

        # 🔹 Save individual trade logs
        trade_log_df = pd.DataFrame(trade_log, columns=["Action", "Date", "Price", "Shares"])
        trade_log_df.to_csv(f"{OUTPUT_FOLDER}/{stock}_trades.csv", index=False)

    # 🔹 Convert results to DataFrame
    df_results = pd.DataFrame(results)

    # 🔹 Save summary results
    summary_file = f"{OUTPUT_FOLDER}/backtest_summary.csv"
    df_results.to_csv(summary_file, index=False)

    # 🔹 Display results in table format
    print("\n📊 **Backtest Results Summary**")
    print(df_results)
    print(f"\n📂 All results saved in: {OUTPUT_FOLDER}/")

    # 🔹 Print additional insights
    print("\n📊 **Backtest Summary Insights**") 
    print(f"📈 Average Return Across All Stocks: {df_results['Total Return (%)'].mean():.2f}%")
    print(f"🏆 Best Performing Stock: {df_results.loc[df_results['Total Return (%)'].idxmax(), 'Stock']} "
        f"({df_results['Total Return (%)'].max():.2f}%)")
    print(f"😢 Worst Performing Stock: {df_results.loc[df_results['Total Return (%)'].idxmin(), 'Stock']} "
        f"({df_results['Total Return (%)'].min():.2f}%)")

