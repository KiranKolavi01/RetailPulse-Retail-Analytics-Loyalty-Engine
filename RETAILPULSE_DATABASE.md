# RetailPulse — Database Implementation Spec

## Tech Stack
- SQLite3 (Python built-in — zero config)
- Database file: db/retail.db (auto-created on first run)
- pandas (for loading CSV data into tables)

---

## How to Create the Database

Run `src/01_setup_db.py` to create all tables. This script is idempotent — it can be run multiple times without error (uses `CREATE TABLE IF NOT EXISTS` for all tables except where drop-and-recreate is needed).

---

## Users Table (Authentication — NEVER DROPPED)

```sql
CREATE TABLE IF NOT EXISTS users (
    user_id   TEXT PRIMARY KEY,
    username  TEXT UNIQUE NOT NULL,
    email     TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,   -- bcrypt hash, NEVER plain text
    created_at TEXT NOT NULL
)
```

- This table is **append-only** — never dropped, never cleared, never overwritten
- Persists across all pipeline runs
- password_hash stores bcrypt-hashed password only

---

## Core Tables (7) — Drop and Recreate on Each ETL Run

All 7 core tables are dropped and recreated every time `02_etl_pipeline.py` runs, so data is always fresh from the CSV files.

### Table: stores
```sql
CREATE TABLE stores (
    store_id    TEXT PRIMARY KEY,
    store_name  TEXT NOT NULL,
    region      TEXT,
    -- all other columns from stores.csv
)
```

### Table: products
```sql
CREATE TABLE products (
    product_id   TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    price        REAL,
    stock_level  INTEGER,
    -- all other columns from products.csv
)
```

### Table: customer_details
```sql
CREATE TABLE customer_details (
    customer_id TEXT PRIMARY KEY,
    first_name  TEXT NOT NULL,
    -- all other columns from customer_details.csv
    loyalty_tier TEXT,  -- Gold / Silver / Bronze (updated by 03_loyalty_rfm.py)
    loyalty_points REAL
)
```

### Table: store_sales_header
```sql
CREATE TABLE store_sales_header (
    transaction_id TEXT PRIMARY KEY,
    store_id       TEXT,
    customer_id    TEXT,
    transaction_date TEXT,
    total_amount   REAL,
    -- all other columns from store_sales_header.csv
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (customer_id) REFERENCES customer_details(customer_id)
)
```

### Table: store_sales_line_items
```sql
CREATE TABLE store_sales_line_items (
    line_item_id   TEXT PRIMARY KEY,
    transaction_id TEXT,
    product_id     TEXT,
    quantity       INTEGER,
    unit_price     REAL,
    -- all other columns from store_sales_line_items.csv
    FOREIGN KEY (transaction_id) REFERENCES store_sales_header(transaction_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
```

### Table: promotion_details
```sql
CREATE TABLE promotion_details (
    promotion_id   TEXT PRIMARY KEY,
    -- all other columns from promotion_details.csv
    discount_pct   REAL  -- must be 0–100
)
```

### Table: loyalty_rules
```sql
CREATE TABLE loyalty_rules (
    rule_id        TEXT PRIMARY KEY,
    tier_name      TEXT,  -- Bronze / Silver / Gold
    points_per_dollar REAL,
    -- all other columns from loyalty_rules.csv
)
```

---

## Rejected Tables (7) — Mirror Tables with reject_reason

Each core table has a matching rejected table. Rejected tables are also dropped and recreated on each ETL run.

The rejected table schema = all columns from the core table + one extra column:

```sql
reject_reason TEXT  -- specific error message explaining why the record was rejected
```

Rejected tables:
- `stores_rejected`
- `products_rejected`
- `customer_details_rejected`
- `store_sales_header_rejected`
- `store_sales_line_items_rejected`
- `promotion_details_rejected`
- `loyalty_rules_rejected`

Example query:
```sql
SELECT * FROM products_rejected;
-- Shows: product_id, all columns, reject_reason
```

---

## Analytics Tables (2) — Drop and Recreate on Each Analytics Run

These tables are dropped and recreated every time `03_loyalty_rfm.py` and `04_predictive.py` run.

### Table: rfm_summary
```sql
CREATE TABLE rfm_summary (
    customer_id         TEXT PRIMARY KEY,
    recency_days        INTEGER,   -- days since last purchase
    frequency           INTEGER,   -- number of transactions
    monetary            REAL,      -- total spend
    loyalty_points      REAL,
    loyalty_tier        TEXT,      -- Bronze / Silver / Gold
    segment             TEXT,      -- HS (High Spender) or AR (At Risk) or NULL
    -- HS takes priority if customer qualifies for both
    FOREIGN KEY (customer_id) REFERENCES customer_details(customer_id)
)
```

Segment logic:
- High Spender (HS): top 20% by monetary value — assigned first, takes priority
- At Risk (AR): no purchase in 30+ days AND not already HS

Loyalty tier logic:
- Gold: ≥ 1000 points
- Silver: ≥ 500 points
- Bronze: < 500 points

### Table: customer_predictions
```sql
CREATE TABLE customer_predictions (
    customer_id              TEXT PRIMARY KEY,
    predicted_next_month_spend REAL,  -- 3-month moving average
    restock_flag             INTEGER, -- 1 = likely to run out of stock, 0 = no
    promotion_sensitivity    TEXT,    -- HIGH / MEDIUM / LOW
    FOREIGN KEY (customer_id) REFERENCES customer_details(customer_id)
)
```

Prediction logic:
- predicted_next_month_spend: 3-month moving average of customer spend
- restock_flag: based on restock threshold logic (flag products likely to run out)
- promotion_sensitivity: HIGH / MEDIUM / LOW classification per customer

---

## Database Behavior Rules

### Drop-and-Recreate Tables (on each pipeline run)
These tables are dropped and fully repopulated every run:
- All 7 core tables
- All 7 rejected tables
- rfm_summary
- customer_predictions

### Append-Only Tables (NEVER dropped)
- `users` — authentication table, persists forever across all runs

### Idempotency
- `01_setup_db.py` can be run multiple times — uses `CREATE TABLE IF NOT EXISTS`
- Running the full pipeline twice gives the same result (except users table which only grows)

### NULL Handling
- All INSERT operations handle NULL values gracefully — no crash on missing optional fields
- Required fields that are NULL → record goes to the *_rejected table with reject_reason = "Required field {field_name} is missing"

### Error Handling
- Missing CSV file → FileError raised, logged, script exits with code 1
- Bad record → DataValidationError caught per row, record inserted into *_rejected table, pipeline continues
- Database connection error → DatabaseError raised, logged, script exits with code 1

---

## Data Loading Pattern (ETL)

```python
# Per-row error handling — pipeline never crashes on bad data
for row in csv_data:
    try:
        validate_and_insert(row)    # insert to core table + write to data/cleaned/
    except DataValidationError as e:
        insert_to_rejected_table(row, reason=str(e))  # insert to *_rejected table + write to data/rejected/
        continue  # keep processing other rows
```

---

## Output Files (database-related)

| Location | Contents |
|---|---|
| db/retail.db | SQLite database with all tables |
| data/cleaned/*.csv | One CSV per core table — clean validated records |
| data/rejected/*.csv | One CSV per rejected table — bad records with reject_reason column |
