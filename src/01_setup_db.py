import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from src.utils.error_handler import handle_exceptions, logger, DatabaseError
except ImportError:
    # Fallback if utils aren't available
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    class DatabaseError(Exception): pass
    def handle_exceptions(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error: {e}")
                raise
        return wrapper

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db', 'retail.db')

@handle_exceptions
def setup_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. CORE TABLES (Union of backend requirements + MD specs)
        core_tables = {
            "stores": {
                "columns": """
                    store_id TEXT PRIMARY KEY,
                    store_name TEXT NOT NULL,
                    region TEXT
                """
            },
            "products": {
                "columns": """
                    product_id TEXT PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    category TEXT,
                    price REAL,
                    stock_level INTEGER
                """
            },
            "loyalty_rules": {
                "columns": """
                    tier TEXT,
                    rule_id TEXT,
                    tier_name TEXT,
                    min_points INTEGER,
                    max_points INTEGER,
                    points_per_dollar REAL,
                    multiplier REAL
                """
            },
            "promotion_details": {
                "columns": """
                    promo_id TEXT,
                    promotion_id TEXT,
                    name TEXT,
                    discount_percentage REAL,
                    discount_pct REAL,
                    start_date TEXT,
                    end_date TEXT
                """
            },
            "customer_details": {
                "columns": """
                    customer_id TEXT PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT,
                    email TEXT,
                    phone TEXT,
                    registration_date TEXT,
                    loyalty_tier TEXT,
                    loyalty_points REAL
                """
            },
            "store_sales_header": {
                "columns": """
                    transaction_id TEXT PRIMARY KEY,
                    store_id TEXT,
                    customer_id TEXT,
                    transaction_date TEXT,
                    total_amount REAL,
                    FOREIGN KEY (store_id) REFERENCES stores(store_id),
                    FOREIGN KEY (customer_id) REFERENCES customer_details(customer_id)
                """
            },
            "store_sales_line_items": {
                "columns": """
                    line_item_id TEXT,
                    transaction_id TEXT,
                    product_id TEXT,
                    quantity INTEGER,
                    price REAL,
                    unit_price REAL,
                    FOREIGN KEY (transaction_id) REFERENCES store_sales_header(transaction_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                """
            }
        }
        
        for name, spec in core_tables.items():
            ddl = f"CREATE TABLE IF NOT EXISTS {name} ({spec['columns']})"
            cursor.execute(ddl)
            
        # 2. REJECTED TABLES
        # The rejected table schema = all columns from the core table + one extra column: reject_reason TEXT
        # Added raw_data and rejected_at for backend compatibility
        rejected_tables = {
            "stores_rejected": """
                store_id TEXT, store_name TEXT, region TEXT,
                raw_data TEXT, reject_reason TEXT, rejected_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """,
            "products_rejected": """
                product_id TEXT, product_name TEXT, category TEXT, price REAL, stock_level INTEGER,
                raw_data TEXT, reject_reason TEXT, rejected_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """,
            "customer_details_rejected": """
                customer_id TEXT, first_name TEXT, last_name TEXT, email TEXT, phone TEXT, registration_date TEXT, loyalty_tier TEXT, loyalty_points REAL,
                raw_data TEXT, reject_reason TEXT, rejected_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """,
            "store_sales_header_rejected": """
                transaction_id TEXT, store_id TEXT, customer_id TEXT, transaction_date TEXT, total_amount REAL,
                raw_data TEXT, reject_reason TEXT, rejected_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """,
            "store_sales_line_items_rejected": """
                line_item_id TEXT, transaction_id TEXT, product_id TEXT, quantity INTEGER, price REAL, unit_price REAL,
                raw_data TEXT, reject_reason TEXT, rejected_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """,
            "promotion_details_rejected": """
                promo_id TEXT, promotion_id TEXT, name TEXT, discount_percentage REAL, discount_pct REAL, start_date TEXT, end_date TEXT,
                raw_data TEXT, reject_reason TEXT, rejected_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """,
            "loyalty_rules_rejected": """
                tier TEXT, rule_id TEXT, tier_name TEXT, min_points INTEGER, max_points INTEGER, points_per_dollar REAL, multiplier REAL,
                raw_data TEXT, reject_reason TEXT, rejected_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """
        }

        for name, columns in rejected_tables.items():
            ddl = f"CREATE TABLE IF NOT EXISTS {name} ({columns})"
            cursor.execute(ddl)
            
        # 3. ANALYTICS TABLES (Matches both backend constraints & MD spec)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rfm_summary (
                customer_id TEXT PRIMARY KEY,
                recency INTEGER,
                recency_days INTEGER,
                frequency INTEGER,
                monetary REAL,
                loyalty_points REAL,
                loyalty_tier TEXT,
                segment TEXT,
                FOREIGN KEY (customer_id) REFERENCES customer_details(customer_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_predictions (
                customer_id TEXT PRIMARY KEY,
                predicted_next_month_spend REAL,
                restock_flag INTEGER,
                promotion_sensitivity TEXT,
                FOREIGN KEY (customer_id) REFERENCES customer_details(customer_id)
            )
        """)

        # Strict Backend Expectation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_restock_predictions (
                product_id TEXT PRIMARY KEY,
                stock_level INTEGER,
                is_restock_needed INTERGER
            )
        """)
        
        # 4. USERS TABLE (Combination of frontend AUTH + MD definition)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.info("Database setup complete.")
        print("Database setup complete.")
        
    except sqlite3.Error as e:
        raise DatabaseError(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_database()
