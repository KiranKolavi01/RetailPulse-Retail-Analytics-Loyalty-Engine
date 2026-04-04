import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta
import uuid

DATA_RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'raw')
os.makedirs(DATA_RAW, exist_ok=True)

def random_dates(start, end, n=10):
    start_u = start.value//10**9
    end_u = end.value//10**9
    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit='s')

# stores.csv
stores = pd.DataFrame({
    'store_id': [f'STORE_{i:03d}' for i in range(1, 6)] + ['STORE_BAD1'],
    'store_name': ['Downtown Retail', 'Uptown Market', 'Suburban Mall', 'City Center', 'Airport Terminal', ''],
    'region': ['North', 'North', 'South', 'East', 'West', 'West']
})
stores.to_csv(os.path.join(DATA_RAW, 'stores.csv'), index=False)

# products.csv
prod_ids = [f'PROD_{i:03d}' for i in range(1, 21)] + ['PROD_BAD1', 'PROD_BAD2']
prod_names = [f'Item {i}' for i in range(1, 21)] + ['Invalid Price Product', 'Negative Stock Product']
categories = list(np.random.choice(['Electronics', 'Clothing', 'Groceries', 'Home'], 20)) + ['Home', 'Electronics']
prices = list(np.round(np.random.uniform(5.0, 500.0, 20), 2)) + [-15.99, 99.99]
stocks = list(np.random.randint(5, 100, 20)) + [50, -5]

products = pd.DataFrame({
    'product_id': prod_ids,
    'product_name': prod_names,
    'category': categories,
    'price': prices,
    'stock_level': stocks
})
products.to_csv(os.path.join(DATA_RAW, 'products.csv'), index=False)

# loyalty_rules.csv
loyalty_rules = pd.DataFrame({
    'tier': ['Bronze', 'Silver', 'Gold'],
    'rule_id': ['R_BRONZE', 'R_SILVER', 'R_GOLD'],
    'tier_name': ['Bronze', 'Silver', 'Gold'],
    'min_points': [0, 500, 1000],
    'max_points': [499, 999, 999999],
    'points_per_dollar': [1.0, 1.5, 2.0],
    'multiplier': [1.0, 1.5, 2.0]
})
loyalty_rules.to_csv(os.path.join(DATA_RAW, 'loyalty_rules.csv'), index=False)

# promotion_details.csv
promotion_details = pd.DataFrame({
    'promo_id': ['PROMO_01', 'PROMO_02'],
    'promotion_id': ['PROMO_01', 'PROMO_02'],
    'name': ['Summer Sale', 'Winter Clearance'],
    'discount_percentage': [15.0, 30.0],
    'discount_pct': [15.0, 30.0],
    'start_date': ['2023-06-01', '2023-12-01'],
    'end_date': ['2023-08-31', '2024-02-28']
})
promotion_details.to_csv(os.path.join(DATA_RAW, 'promotion_details.csv'), index=False)

# customer_details.csv
customers = pd.DataFrame({
    'customer_id': [f'CUST_{i:03d}' for i in range(1, 51)],
    'first_name': [f'First{i}' for i in range(1, 51)],
    'last_name': [f'Last{i}' for i in range(1, 51)],
    'email': [f'cust{i}@example.com' for i in range(1, 51)],
    'phone': [f'555-{random.randint(1000, 9999)}' for _ in range(50)],
    'registration_date': random_dates(pd.to_datetime('2022-01-01'), pd.to_datetime('2023-12-31'), 50).strftime('%Y-%m-%d'),
    'loyalty_tier': np.random.choice(['Bronze', 'Silver', 'Gold'], 50),
    'loyalty_points': np.random.randint(0, 1500, 50)
})
customers.to_csv(os.path.join(DATA_RAW, 'customer_details.csv'), index=False)

# store_sales_header.csv
num_transactions = 200
transactions = random_dates(pd.to_datetime('2023-01-01'), pd.to_datetime('today'), num_transactions)
sales_header = pd.DataFrame({
    'transaction_id': [f'TXN_{i:04d}' for i in range(1, num_transactions + 1)],
    'store_id': np.random.choice(stores['store_id'], num_transactions),
    'customer_id': np.random.choice(customers['customer_id'], num_transactions),
    'transaction_date': transactions.strftime('%Y-%m-%d %H:%M:%S'),
    'total_amount': np.round(np.random.uniform(20.0, 500.0, num_transactions), 2)
})
sales_header.to_csv(os.path.join(DATA_RAW, 'store_sales_header.csv'), index=False)

# store_sales_line_items.csv
line_items = []
for txn_id in sales_header['transaction_id']:
    num_items = random.randint(1, 5)
    selected_prods = products.sample(n=num_items)
    for _, prod in selected_prods.iterrows():
        qty = random.randint(1, 3)
        price = prod['price']
        line_items.append({
            'line_item_id': str(uuid.uuid4()),
            'transaction_id': txn_id,
            'product_id': prod['product_id'],
            'quantity': qty,
            'price': price,
            'unit_price': price
        })
sales_line_items = pd.DataFrame(line_items)
sales_line_items.to_csv(os.path.join(DATA_RAW, 'store_sales_line_items.csv'), index=False)

print("Generated mock data successfully.")
