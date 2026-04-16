import pandas as pd
import numpy as np

# File configuration
price_files = ['prices_round_1_day_0.csv', 'prices_round_1_day_-1.csv', 'prices_round_1_day_-2.csv']
trade_files = ['trades_round_1_day_0.csv', 'trades_round_1_day_-1.csv', 'trades_round_1_day_-2.csv']

def run_comprehensive_analysis():
    print("--- Loading Data ---")
    try:
        price_dfs = [pd.read_csv(f, sep=';') for f in price_files]
        df_p = pd.concat(price_dfs).sort_values(['day', 'timestamp'])
        
        trade_dfs = [pd.read_csv(f, sep=';') for f in trade_files]
        df_t = pd.concat(trade_dfs).sort_values(['timestamp'])
    except FileNotFoundError as e:
        print(f"Error: Could not find files. {e}")
        return

    products = df_p['product'].unique()

    # 1. FAIR VALUE & VOLATILITY
    print("\n--- Section 1: Price Statistics (Fair Value) ---")
    for prod in products:
        data = df_p[df_p['product'] == prod]
        print(f"\nProduct: {prod}")
        print(f"  Overall Mean Mid-Price: {data['mid_price'].mean():.2f}")
        print(f"  Standard Deviation:     {data['mid_price'].std():.2f}")
        print(f"  Mean Spread:           {(data['ask_price_1'] - data['bid_price_1']).mean():.2f}")
        
        # Check for drift across days
        day_means = data.groupby('day')['mid_price'].mean()
        print(f"  Daily Means:\n{day_means.to_string()}")

    # 2. LEAD-LAG PATTERN SEARCH (Updated for Pandas 3.0+)
    print("\n--- Section 2: Hidden Pattern (Lead-Lag) ---")
    pivot_p = df_p.pivot_table(index=['day', 'timestamp'], columns='product', values='mid_price')
    pivot_p = pivot_p.ffill() # Fixed the error here
    
    if len(products) >= 2:
        p1, p2 = products[0], products[1]
        print(f"Checking correlation between {p1} and {p2}:")
        for lag in range(-3, 4):
            corr = pivot_p[p1].corr(pivot_p[p2].shift(lag))
            suffix = " (Lag)" if lag > 0 else " (Lead)" if lag < 0 else " (Sync)"
            print(f"  Correlation at lag {lag:2}: {corr: .4f}{suffix}")

    # 3. TREND CALCULATION
    print("\n--- Section 3: Trend Strength ---")
    for prod in products:
        data = pivot_p[prod].values
        # Simple check: is the price generally higher at the end than the start?
        diff = data[-1] - data[0]
        print(f"Product: {prod} | Total Growth over 3 days: {diff:.2f} points")

    # 4. TRADE MOOD (IMBALANCE)
    print("\n--- Section 4: The 'Mood' (Trade Analysis) ---")
    for prod in products:
        t_data = df_t[df_t['symbol'] == prod]
        if not t_data.empty:
            avg_vol = t_data['quantity'].mean()
            print(f"Product: {prod}")
            print(f"  Average Trade Size: {avg_vol:.2f}")
            # If buyer/seller info is missing, we look at trade price vs mid price
            # We'll need to merge for this, but simple trade price stats help:
            print(f"  Trade Price StdDev: {t_data['price'].std():.2f}")

    # 5. ORDER BOOK LIQUIDITY (The "Tipping Point")
    print("\n--- Section 5: Liquidity Clusters ---")
    for prod in products:
        data = df_p[df_p['product'] == prod]
        avg_bid_vol = data['bid_volume_1'].mean()
        avg_ask_vol = data['ask_volume_1'].mean()
        print(f"{prod}: Avg Depth - Bid: {avg_bid_vol:.1f}, Ask: {avg_ask_vol:.1f}")

if __name__ == "__main__":
    run_comprehensive_analysis()