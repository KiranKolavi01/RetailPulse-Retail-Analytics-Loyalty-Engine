# RetailPulse — Backend Implementation Spec

## Tech Stack
- Python 3.8+
- FastAPI
- SQLite3 (via Python's built-in sqlite3 module)
- pandas
- matplotlib
- pytest (96 unit tests)
- bcrypt (for auth password hashing)
- uvicorn

---

## Project Structure

```
RetailPulse/
├── data/
│   ├── raw/                        # Source CSV files (input)
│   ├── cleaned/                    # Validated clean records (exported CSVs)
│   └── rejected/                   # Bad records with reasons (exported CSVs)
├── db/
│   └── retail.db                   # SQLite database (auto-created)
├── src/
│   ├── 01_setup_db.py              # Database schema creation
│   ├── 02_etl_pipeline.py          # ETL: validate, clean, load
│   ├── 03_loyalty_rfm.py           # Loyalty points + RFM segmentation
│   ├── 04_predictive.py            # Predictive analytics
│   ├── 05_dashboard.py             # Static matplotlib dashboard
│   ├── generate_er_diagram.py      # ER diagram generator
│   └── utils/
│       └── error_handler.py        # Centralized error handling
├── tests/
│   ├── test_setup_db.py            # 14 tests
│   ├── test_etl_pipeline.py        # 27 tests
│   ├── test_loyalty_rfm.py         # 22 tests
│   └── test_predictive.py          # 33 tests
├── output/
│   ├── dashboard.png               # Combined 4-chart dashboard
│   └── chart*.png                  # Individual chart images
├── logs/
│   └── retailpulse_*.log           # Daily rotating log files
├── diagrams/
│   └── er_diagram.png              # Database ER diagram
├── main.py                         # FastAPI app + pipeline orchestration
└── README.md
```

---

## Input Data Files (must exist in data/raw/)

| File | Records | Description |
|---|---|---|
| stores.csv | 5 | Store locations and regions |
| products.csv | 49 | Product catalog with pricing |
| loyalty_rules.csv | 5 | Point calculation rules by tier |
| promotion_details.csv | 10 | Promotional campaigns |
| customer_details.csv | 199 | Customer profiles |
| store_sales_header.csv | ~2000 | Transaction headers |
| store_sales_line_items.csv | ~5000 | Individual items per transaction |

---

## Pipeline — 5 Scripts

Run in this exact sequence:

### Script 1 — src/01_setup_db.py
- Creates all database tables: 7 core tables, 7 rejected tables, 2 analytics tables
- Idempotent: can be run multiple times without error (CREATE TABLE IF NOT EXISTS)
- Prints log message on completion

### Script 2 — src/02_etl_pipeline.py
- Reads all 7 CSV files from data/raw/
- Runs all 5 validation types on every record (see Data Quality Validation below)
- Clean records → inserted into core tables AND exported to data/cleaned/*.csv
- Bad records → inserted into *_rejected tables AND exported to data/rejected/*.csv with reject_reason
- Individual row errors do not crash the pipeline — continue processing other rows
- Prints log message on completion

### Script 3 — src/03_loyalty_rfm.py
- Reads from cleaned core tables in db/retail.db
- Calculates loyalty points per customer using loyalty_rules.csv tiers
- Assigns loyalty tier: Gold (≥1000 points), Silver (≥500 points), Bronze (<500 points)
- Calculates RFM scores: Recency, Frequency, Monetary per customer
- Identifies customer segments:
  - High Spender (HS): top 20% by monetary value — takes priority
  - At Risk (AR): no purchase in 30+ days
- Writes results to rfm_summary table
- Prints log message on completion

### Script 4 — src/04_predictive.py
- Reads from rfm_summary and core tables
- Spend Forecasting: predicts next month spend using 3-month moving averages
- Restock Predictions: flags products likely to run out of stock using restock threshold logic
- Promotion Sensitivity: classifies each customer as HIGH / MEDIUM / LOW responder
- Writes results to customer_predictions table
- Prints log message on completion

### Script 5 — src/05_dashboard.py
- Reads from all tables
- Generates static matplotlib charts:
  - Sales trends
  - Customer loyalty distribution
  - At-risk customer alerts
  - Top products analysis
- Saves combined 4-chart dashboard to output/dashboard.png
- Saves individual charts to output/chart*.png
- Prints log message on completion

---

## How to Run

```bash
# Step 1
python src/01_setup_db.py

# Step 2
python src/02_etl_pipeline.py

# Step 3
python src/03_loyalty_rfm.py

# Step 4
python src/04_predictive.py

# Step 5
python src/05_dashboard.py

# Total time: ~30 seconds
```

---

## Data Quality Validation (ETL — 5 Types)

### 1. Required Fields Check
These columns cannot be empty:
- store_id, product_id, customer_id, transaction_id
- store_name, product_name, first_name

### 2. Data Type Validation
- Numbers must be numeric (prices, quantities, amounts)
- Dates must be valid date formats
- IDs are normalized (float → string conversion)

### 3. Business Rules
- Prices and quantities must be non-negative
- Stock levels must be valid integers
- Percentages must be between 0–100

### 4. Character Stripping
Automatically removes special characters from amount fields:
- Currency symbols: $, ₹, £, €
- Formatting characters: , %

### 5. Rejection Tracking
Bad records are never deleted — they go to *_rejected tables with a specific reject_reason message. Example: `$100 → 100` after stripping.

---

## Error Handling

### Custom Exception Hierarchy (src/utils/error_handler.py)

```
RetailPulseError (base)
├── DatabaseError       # Connection, query, table issues
├── FileError           # Missing files, permission errors
├── ETLError            # Validation, transformation failures
├── AnalyticsError      # Calculation, prediction errors
├── DataValidationError # Invalid data format/values
└── ConfigurationError  # Missing config, invalid settings
```

### Features
- Daily rotating logs saved to logs/retailpulse_YYYYMMDD.log
- `@handle_exceptions` decorator for consistent error handling on all functions
- `@retry_on_error` decorator for transient failures
- `validate_file_exists()` and `validate_directory_exists()` utilities
- All scripts return exit code 0 (success) or 1 (error)
- Graceful row-level error recovery: individual bad rows go to rejected, pipeline continues

---

## Unit Tests (96 total)

```bash
# Run all 96 tests
python -m pytest tests/ -v

# Run specific module
python -m pytest tests/test_etl_pipeline.py -v

# With coverage
python -m pytest tests/ --cov=src

# Stop on first failure
python -m pytest tests/ -x

# Run by pattern
python -m pytest tests/ -k "loyalty"

# Generate HTML report
python -m pytest tests/ --html=report.html
```

| Module | Tests | What It Covers |
|---|---|---|
| test_setup_db.py | 14 | Table creation, constraints, idempotency, defaults |
| test_etl_pipeline.py | 27 | Validation, type casting, CSV ingestion, null handling, negatives, incremental load, special char stripping |
| test_loyalty_rfm.py | 22 | Points calculation, tier boundaries, RFM recency, at-risk flagging (>30 days), high spender (top 20%) |
| test_predictive.py | 33 | 3-month moving average, restock threshold, promotion sensitivity, edge cases (zero history, large values, decimals) |

---

## FastAPI App (main.py)

### Authentication Endpoints

**POST /auth/signup**
- Body: `{ "username": str, "email": str, "password": str }`
- Hash password with bcrypt before storing in users table
- Return 400 if username or email already exists
- Return `{ "status": "success", "username": str }` on success

**POST /auth/signin**
- Body: `{ "username": str, "password": str }`
- Verify bcrypt hash
- Return 401 if credentials invalid
- Return `{ "status": "success", "username": str }` on success

### Pipeline Endpoints

**POST /run-pipeline**
- Runs all 5 scripts in sequence: setup_db → etl → loyalty_rfm → predictive → dashboard
- Prints step-by-step log after each script completes
- Returns `{ "status": "success", "steps_completed": [...] }`
- Returns error message if any step fails

**GET /pipeline-status**
- Returns last run timestamp and status

### Data Endpoints (all return JSON, NaN replaced with empty string)

**GET /stores** — returns stores table as JSON  
**GET /products** — returns products table as JSON  
**GET /customers** — returns customer_details table as JSON  
**GET /sales-header** — returns store_sales_header as JSON  
**GET /sales-line-items** — returns store_sales_line_items as JSON  
**GET /rfm-summary** — returns rfm_summary table as JSON  
**GET /customer-predictions** — returns customer_predictions table as JSON  
**GET /rejected/{table_name}** — returns specified *_rejected table as JSON; 404 if table doesn't exist  

### Visualization Endpoints

**GET /visualizations/{filename}**
- Serves PNG files from output/ directory
- Path traversal protection: validate filename matches `^[\w\-]+\.png$`, block any `../` attempts
- Return 404 if file not found or pattern doesn't match

### NaN Safety Rule
ALL data endpoints must replace NaN / None with empty string `""` before returning JSON. Use `df.where(pd.notnull(df), "")` or equivalent. Never return raw NaN in JSON responses.

### CORS
Enable CORS middleware allowing all origins so the Streamlit frontend can connect.

### Startup
Run with uvicorn when executed directly:
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## requirements.txt

```
fastapi
uvicorn[standard]
pandas
matplotlib
bcrypt
pytest
pytest-cov
pytest-html
```

---

## Output Files

| Location | Contents |
|---|---|
| db/retail.db | SQLite database with all tables |
| data/cleaned/*.csv | Validated clean records |
| data/rejected/*.csv | Rejected records with reasons |
| output/dashboard.png | Combined 4-chart dashboard |
| output/chart*.png | Individual chart images |
| logs/retailpulse_*.log | Execution logs |
| diagrams/er_diagram.png | Database ER diagram |

---

## Re-runnable Behavior

- Running the pipeline again always reads fresh input from data/raw/
- Core tables are cleared and repopulated on each ETL run
- rfm_summary and customer_predictions are cleared and repopulated on each analytics run
- Visualizations are regenerated on each dashboard run
- users table is NEVER dropped or cleared — it is append-only
- logs/ appends to daily log files — never deletes logs
