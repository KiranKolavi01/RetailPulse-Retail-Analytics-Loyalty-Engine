# RetailPulse — Frontend Implementation Spec

## Tech Stack
- Python
- Streamlit
- HTML + CSS (for UI polish only — no React, no Vue)
- Plotly (for interactive charts)
- matplotlib (for static chart display)

---

## Authentication

### Page: Sign Up
- Fields: Username, Email, Password, Confirm Password
- Client-side validation: all fields required, password must match confirm password, email must contain @
- On submit: POST to `/auth/signup`
- On success: redirect to Sign In page, show success message
- On error (username/email taken): show specific error message below the form
- Link at bottom: "Already have an account? Sign In"

### Page: Sign In
- Fields: Username, Password
- On submit: POST to `/auth/signin`
- On success: store username in `st.session_state["username"]`, redirect to Dashboard (Run Pipeline page)
- On error (invalid credentials): show error message below the form
- Link at bottom: "Don't have an account? Sign Up"

### Auth State Management
- At the very top of app.py, before any page routing: check `st.session_state.get("username")` — if not set, show Sign In page only
- Never render any dashboard page when user is not signed in
- Sign Out button in sidebar: clears `st.session_state["username"]` and all session state, redirects to Sign In
- Initialize `st.session_state["username"] = None` at startup if not already set

---

## Page Refresh Persistence

Use Streamlit query params to persist the current page across browser refreshes. Implement in app.py:

```python
# At top of navigation logic — read page from URL first
params = st.query_params
if "page" in params:
    st.session_state["current_page"] = params["page"]
elif "current_page" not in st.session_state:
    st.session_state["current_page"] = "Run Pipeline"

# Every navigation click must call this function
def navigate_to(page_name):
    st.session_state["current_page"] = page_name
    st.query_params["page"] = page_name
```

- Every sidebar navigation button click must call `navigate_to(page_name)`
- URL bar must reflect current page: `?page=Sales+Trends` etc.
- On browser refresh, app loads the page shown in the URL — not always the default page
- Sidebar must highlight the active page after refresh

---

## Summary Card Rules (fixes N/A bug)

On every page that shows numeric summary cards:
- Convert all columns to numeric using `pd.to_numeric(col, errors="coerce")` before computing averages or sums
- Use f-strings only — never `"string" + float` concatenation
- If result is NaN after computation, show `0.0` instead of `N/A`
- Round all displayed averages to 1 decimal place

---

## API Configuration

- Backend base URL: configurable, default `http://localhost:8000`
- On app startup, call `GET /` to verify backend is reachable
- If backend is unreachable: show a red error banner at the top of every page: "Backend not reachable at {url}. Please start the FastAPI server."
- Distinguish between network errors (connection refused) and API errors (4xx/5xx) in error messages

---

## Navigation

- Sidebar navigation showing all pages
- Active page highlighted in sidebar
- After browser refresh, sidebar highlights the correct active page (via query params)
- Sign Out button at the bottom of the sidebar (only shown when signed in)

---

## Pages

### Page 1 — Run Pipeline
- Button: "Run Full Pipeline"
- On click: POST to `/run-pipeline`
- Disable the button while pipeline is executing
- Display step-by-step progress logs as they are returned:
  - Step 1: Setup DB
  - Step 2: ETL Pipeline
  - Step 3: Loyalty & RFM
  - Step 4: Predictive Analytics
  - Step 5: Dashboard Generation
- Show success message when all steps complete
- Show error message if any step fails, with the step name that failed
- Loading indicator while pipeline is running

### Page 2 — Sales Trends
- Fetch data from `GET /sales-header`
- Loading indicator while fetching
- Error message if backend returns error
- Summary cards: Total Transactions, Total Revenue, Avg Transaction Value, Total Stores Active
  - All cards use `pd.to_numeric(errors="coerce")`, f-strings, 0.0 fallback
- Interactive Plotly chart: sales over time (line chart, x=date, y=revenue)
- Interactive table: all sales header records with sort and filter

### Page 3 — Customer Loyalty Distribution
- Fetch data from `GET /rfm-summary`
- Loading indicator while fetching
- Error message if backend returns error
- Summary cards: Total Customers, Gold Tier Count, Silver Tier Count, Bronze Tier Count
- Interactive Plotly chart: loyalty tier distribution (pie or bar chart)
- Interactive table: all RFM records with sort and filter — columns include customer_id, loyalty tier, recency, frequency, monetary, segment (HS/AR)

### Page 4 — At-Risk Customer Alerts
- Fetch data from `GET /rfm-summary`
- Loading indicator while fetching
- Error message if backend returns error
- Filter to show only At Risk (AR) customers — those with no purchase in 30+ days
- Red alert banner above table: "⚠ {count} customers are at risk of churn. Retention campaigns recommended."
- Summary cards: Total At-Risk Customers, Avg Days Since Last Purchase, Total Revenue at Risk
- Interactive table: at-risk customers with sort and filter
- Color-code rows: customers with >60 days inactivity in darker red vs 30–60 days in amber

### Page 5 — Top Products Analysis
- Fetch data from `GET /sales-line-items` and `GET /products`
- Loading indicator while fetching
- Error message if backend returns error
- Summary cards: Total Products, Top Product by Revenue, Top Product by Quantity, Avg Product Price
- Interactive Plotly chart: top 10 products by revenue (horizontal bar chart)
- Interactive table: all products with sales data, sort and filter

### Page 6 — RFM Segmentation View
- Fetch data from `GET /rfm-summary`
- Loading indicator while fetching
- Error message if backend returns error
- Summary cards: Total Customers, High Spenders (HS) count, At Risk (AR) count, Avg RFM Score
- Interactive Plotly scatter chart: Frequency vs Monetary, colored by segment (HS = gold, AR = red)
- Interactive table: full RFM data with sort and filter
- Reference card: explain what HS and AR mean and the criteria (top 20% monetary = HS, >30 days no purchase = AR, HS takes priority)

### Page 7 — Predictive Analytics
- Fetch data from `GET /customer-predictions`
- Loading indicator while fetching
- Error message if backend returns error
- Summary cards: Customers with Predictions, Avg Predicted Spend, Restock Flags Count, High Promotion Sensitivity Count
- Interactive Plotly chart: predicted spend distribution (histogram)
- Interactive table: all customer predictions with sort and filter — columns include customer_id, predicted_next_month_spend, restock_flag, promotion_sensitivity (HIGH/MEDIUM/LOW)
- Color-code promotion_sensitivity: HIGH = red, MEDIUM = amber, LOW = green
- Color-code restock_flag: True = red, False = green

### Page 8 — Rejected Records
- Fetch data from `GET /rejected/{table_name}`
- Dropdown selector: choose which rejected table to view (stores_rejected, products_rejected, customer_details_rejected, store_sales_header_rejected, store_sales_line_items_rejected, promotion_details_rejected, loyalty_rules_rejected)
- Loading indicator while fetching
- Error message if backend returns error or table doesn't exist
- Summary card: Total Rejected Records for selected table
- Interactive table: rejected records with sort and filter — must show reject_reason column prominently
- Color-code reject_reason column by error type if possible

### Page 9 — Visualizations
- Display all static chart images from backend
- Fetch each chart individually from `GET /visualizations/{filename}`:
  - `dashboard.png` — Combined 4-chart dashboard
  - Individual `chart*.png` files
- Loading indicator for each chart while fetching
- Per-chart error message if a single chart fails to load (do not hide all charts if one fails)
- Display charts in a clean grid layout

---

## UI Design Rules

- Clean, minimal, professional design suitable for a retail business dashboard
- Consistent typography throughout all pages
- Appropriate spacing between elements — no cramped layouts
- Professional color scheme
- Clear visual hierarchy — page titles, section headers, data tables
- Responsive layout across screen sizes
- HTML + CSS used only for polish (badges, color-coded cells, custom banners) — all routing and data fetching stays in Python/Streamlit

---

## Error Handling Rules (apply to every page)

- Every API call wrapped in try/except
- Network errors (connection refused): "Cannot connect to backend. Is the FastAPI server running at {url}?"
- API errors (4xx/5xx): show the HTTP status code and message
- Empty data: show "No data available. Run the pipeline first." instead of an empty table
- Never show a raw Python traceback to the user
- Log detailed error info to console for debugging

---

## Interactive Table Rules (apply to every table page)

- Sort: clicking column headers sorts ascending/descending
- Filter: search/filter input above the table
- All tables must handle empty dataframes gracefully (show message, not error)
- All numeric columns: `pd.to_numeric(errors="coerce")` applied before display
