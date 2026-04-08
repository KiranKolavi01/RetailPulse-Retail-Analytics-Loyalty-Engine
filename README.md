# RetailPulse — Retail Analytics & Loyalty Engine

A complete data pipeline for retail analytics. Drop in raw CSV files, get clean validated data, customer loyalty scores, RFM segments, predictive insights, and an interactive dashboard — all powered by Python and SQLite with zero external database setup.

<img width="1456" height="829" alt="Screenshot 2026-04-05 at 8 09 37 pm" src="https://github.com/user-attachments/assets/27fa5994-448a-452c-95b3-9080f9fe08fa" />


---

## What It Does

RetailPulse takes messy retail data and turns it into actionable business intelligence:

- **Cleans and validates** raw sales data from CSV files, tracking every rejected record with a specific reason
- **Calculates loyalty points** for each customer based on configurable tier rules
- **Segments customers** using RFM analysis — identifies high-value customers and those at risk of churning
- **Predicts** next month spend, flags products likely to run out of stock, and classifies promotion sensitivity
- **Visualizes everything** through an interactive Streamlit dashboard and static matplotlib charts

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| Backend API | FastAPI |
| Database | SQLite3 |
| Data Processing | pandas |
| Visualization | Streamlit, Plotly, matplotlib |
| Testing | pytest (96 unit tests) |

---

## Project Structure

```
RetailPulse/
├── data/
│   ├── raw/              # Put your CSV files here
│   ├── cleaned/          # Clean validated records (auto-generated)
│   └── rejected/         # Bad records with rejection reasons (auto-generated)
├── db/
│   └── retail.db         # SQLite database (auto-created)
├── src/
│   ├── 01_setup_db.py    # Creates all database tables
│   ├── 02_etl_pipeline.py # Validates, cleans, and loads data
│   ├── 03_loyalty_rfm.py  # Loyalty points + RFM segmentation
│   ├── 04_predictive.py   # Predictive analytics
│   ├── 05_dashboard.py    # Static matplotlib charts
│   └── utils/
│       └── error_handler.py
├── Frontend/
│   ├── app.py             # Main Streamlit app
│   ├── client.py          # API client
│   ├── custom_styles.py   # Design system
│   ├── helpers.py         # Shared utilities
│   ├── config.py          # Configuration
│   └── pages/             # One file per dashboard page
├── tests/                 # 96 unit tests
├── output/                # Generated charts
├── logs/                  # Daily rotating logs
└── main.py                # FastAPI app
```

---

## Getting Started

### 1. Install dependencies

```bash
pip install pandas matplotlib streamlit plotly fastapi uvicorn pytest bcrypt
```

### 2. Add your data files

Place these CSV files in `data/raw/`:

```
stores.csv
products.csv
customer_details.csv
promotion_details.csv
loyalty_rules.csv
store_sales_header.csv
store_sales_line_items.csv
```

### 3. Run the pipeline

```bash
# Step 1 — Create database tables
python src/01_setup_db.py

# Step 2 — Validate and load data
python src/02_etl_pipeline.py

# Step 3 — Calculate loyalty points and RFM segments
python src/03_loyalty_rfm.py

# Step 4 — Run predictive analytics
python src/04_predictive.py

# Step 5 — Generate static charts
python src/05_dashboard.py
```

Total time: ~30 seconds

### 4. Start the backend API

```bash
python main.py
```

API runs at `http://localhost:8000`

### 5. Launch the dashboard

```bash
streamlit run Frontend/app.py
```

Open your browser at `http://localhost:8501`

---

## Dashboard Pages

| Page | What It Shows |
|---|---|
| Run Pipeline | Trigger the full pipeline and watch step-by-step logs |
| Sales Trends | Revenue over time, transaction counts, store performance |
| Customer Loyalty | Loyalty tier distribution — Gold, Silver, Bronze |
| At-Risk Alerts | Customers with no purchase in 30+ days |
| Top Products | Best performing products by revenue and quantity |
| RFM Segmentation | Customer segments — High Spenders and At-Risk |
| Predictive Analytics | Predicted spend, restock flags, promotion sensitivity |
| Rejected Records | Every bad record with the exact reason it was rejected |
| Visualizations | Static matplotlib dashboard and individual charts |

---

## Data Validation

The ETL pipeline checks every record against 5 rules before accepting it:

1. **Required fields** — transaction ID, customer ID, product ID, store ID cannot be empty
2. **Data types** — prices must be numeric, dates must be valid dates
3. **Business rules** — prices and quantities must be non-negative, percentages between 0–100
4. **Character stripping** — automatically removes `$`, `₹`, `£`, `€`, `,`, `%` from amount fields
5. **Rejection tracking** — bad records go to `*_rejected` tables with a specific reason, clean data keeps flowing

Bad records are never silently deleted. You can always see exactly what was wrong:

```sql
SELECT * FROM products_rejected;
-- Shows every rejected product with reject_reason column
```

---

## Customer Segments

| Segment | Criteria | Priority |
|---|---|---|
| High Spender (HS) | Top 20% by total spend | First — takes priority |
| At Risk (AR) | No purchase in 30+ days | Only if not already HS |

## Loyalty Tiers

| Tier | Points Required |
|---|---|
| Gold | 1000+ points |
| Silver | 500–999 points |
| Bronze | Under 500 points |

---

## Predictive Analytics

All predictions use logic-based calculations — no external ML libraries required:

- **Spend forecast** — 3-month moving average of each customer's historical spend
- **Restock flags** — products flagged when stock levels fall below restock threshold
- **Promotion sensitivity** — customers classified as HIGH / MEDIUM / LOW based on purchase response to past promotions

---

## Running Tests

```bash
# Run all 96 tests
python -m pytest tests/ -v

# Run a specific module
python -m pytest tests/test_etl_pipeline.py -v

# Run with coverage report
python -m pytest tests/ --cov=src

# Generate HTML report
python -m pytest tests/ --html=report.html
```

| Test File | Tests | Covers |
|---|---|---|
| test_setup_db.py | 14 | Table creation, constraints, idempotency |
| test_etl_pipeline.py | 27 | Validation, type casting, special characters, nulls |
| test_loyalty_rfm.py | 22 | Points calculation, tier boundaries, RFM logic |
| test_predictive.py | 33 | Moving averages, restock logic, promo sensitivity |

---

## API Endpoints

Once `python main.py` is running:

| Method | Endpoint | Returns |
|---|---|---|
| POST | `/run-pipeline` | Runs all 5 pipeline steps |
| GET | `/stores` | All store records |
| GET | `/products` | All product records |
| GET | `/customers` | All customer records |
| GET | `/sales-header` | Transaction headers |
| GET | `/sales-line-items` | Line items per transaction |
| GET | `/rfm-summary` | RFM scores and segments |
| GET | `/customer-predictions` | Predictive analytics results |
| GET | `/rejected/{table_name}` | Rejected records for any table |
| GET | `/visualizations/{filename}` | Static chart images |

---

## Output Files

After running the full pipeline:

| Location | Contents |
|---|---|
| `db/retail.db` | SQLite database with all tables |
| `data/cleaned/*.csv` | One CSV per table — validated clean records |
| `data/rejected/*.csv` | Rejected records with reject_reason column |
| `output/dashboard.png` | Combined 4-chart matplotlib dashboard |
| `output/chart*.png` | Individual chart images |
| `logs/retailpulse_*.log` | Daily rotating execution logs |

---

## Repository

[github.com/KiranKolavi01/RetailPulse-Retail-Analytics-Loyalty-Engine](https://github.com/KiranKolavi01/RetailPulse-Retail-Analytics-Loyalty-Engine.git)
