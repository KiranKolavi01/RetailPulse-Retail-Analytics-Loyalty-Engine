import sqlite3
import os
import sys

# Ensure error_handler is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from src.utils.error_handler import handle_exceptions, logger, DatabaseError
except ImportError:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db', 'retail.db')

@handle_exceptions
def setup_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. CORE TABLES
        core_tables = {
            "stores": """
                CREATE TABLE IF NOT EXISTS stores (
                    store_id TEXT PRIMARY KEY,
                    store_name TEXT NOT NULL,
                    region TEXT
                )
            """,
            "products": """
                CREATE TABLE IF NOT EXISTS products (
                    product_id TEXT PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    category TEXT,
                    price REAL,
                    stock_level INTEGER
                )
            """,
            "loyalty_rules": """
                CREATE TABLE IF NOT EXISTS loyalty_rules (
                    tier TEXT PRIMARY KEY,
                    min_points INTEGER,
                    max_points INTEGER,
                    multiplier REAL
                )
            """,
            "promotion_details": """
                CREATE TABLE IF NOT EXISTS promotion_details (
                    promo_id TEXT PRIMARY KEY,
                    name TEXT,
                    discount_percentage REAL,
                    start_date TEXT,
                    end_date TEXT
                )
            """,
            "customer_details": """
                CREATE TABLE IF NOT EXISTS customer_details (
                    customer_id TEXT PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT,
                    email TEXT,
                    phone TEXT,
                    registration_date TEXT
                )
            """,
            "store_sales_header": """
                CREATE TABLE IF NOT EXISTS store_sales_header (
                    transaction_id TEXT PRIMARY KEY,
                    store_id TEXT,
                    customer_id TEXT,
                    transaction_date TEXT,
                    total_amount REAL
                )
            """,
            "store_sales_line_items": """
                CREATE TABLE IF NOT EXISTS store_sales_line_items (
                    transaction_id TEXT,
                    product_id TEXT,
                    quantity INTEGER,
                    price REAL
                )
            """
        }
        
        for name, ddl in core_tables.items():
            cursor.execute(ddl)
            
        # 2. REJECTED TABLES
        for name in core_tables.keys():
            rejected_table_name = f"{name}_rejected"
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {rejected_table_name} (
                    raw_data TEXT,
                    reject_reason TEXT,
                    rejected_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
        # 3. ANALYTICS TABLES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rfm_summary (
                customer_id TEXT PRIMARY KEY,
                recency INTEGER,
                frequency INTEGER,
                monetary REAL,
                loyalty_points INTEGER,
                loyalty_tier TEXT,
                segment TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_predictions (
                customer_id TEXT PRIMARY KEY,
                predicted_next_month_spend REAL,
                promotion_sensitivity TEXT
            )
        """)
        
        # We also need a place to put restock predictions for products
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_restock_predictions (
                product_id TEXT PRIMARY KEY,
                stock_level INTEGER,
                is_restock_needed INTERGER
            )
        """)
        
        # 4. USERS TABLE (Append-only)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
