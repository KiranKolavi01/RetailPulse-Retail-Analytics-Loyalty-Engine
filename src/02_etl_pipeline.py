import pandas as pd
import sqlite3
import os
import sys
import json
from datetime import datetime

# Ensure error_handler is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from src.utils.error_handler import handle_exceptions, logger, ETLError, FileError
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW = os.path.join(BASE_DIR, 'data', 'raw')
DATA_CLEAN = os.path.join(BASE_DIR, 'data', 'cleaned')
DATA_REJECT = os.path.join(BASE_DIR, 'data', 'rejected')
DB_PATH = os.path.join(BASE_DIR, 'db', 'retail.db')

FILES_EXPECTED = [
    'stores.csv',
    'products.csv',
    'loyalty_rules.csv',
    'promotion_details.csv',
    'customer_details.csv',
    'store_sales_header.csv',
    'store_sales_line_items.csv'
]

REQUIRED_FIELDS = {
    'store_id', 'product_id', 'customer_id', 'transaction_id',
    'store_name', 'product_name', 'first_name'
}

def clean_and_strip_characters(val):
    if pd.isna(val):
        return val
    if isinstance(val, str):
        # Character Stripping - Rule 4
        chars_to_remove = ['$', '₹', '£', '€', ',', '%']
        for c in chars_to_remove:
            val = val.replace(c, '')
        return val.strip()
    return val

def validate_row(row, table_name):
    """Returns (is_valid, reject_reason, cleaned_row)"""
    cleaned_row = row.copy()
    reject_reasons = []

    # 4. Character Stripping
    for col in cleaned_row.index:
        cleaned_row[col] = clean_and_strip_characters(cleaned_row[col])

    # 1. Required Fields Check
    for col in cleaned_row.index:
        if col in REQUIRED_FIELDS:
            if pd.isna(cleaned_row[col]) or str(cleaned_row[col]).strip() == "":
                reject_reasons.append(f"Required field '{col}' is empty")

    # 2. Data Type Validation & IDs to strings
    for col in cleaned_row.index:
        val = cleaned_row[col]
        if pd.isna(val) or val == "":
            continue
            
        if col.endswith('_id'):
            # force to string representing int/float without decimals if possible
            try:
                if isinstance(val, float):
                    cleaned_row[col] = str(int(val))
                else:
                    cleaned_row[col] = str(val)
            except ValueError:
                cleaned_row[col] = str(val)

        if col in ['price', 'total_amount', 'discount_percentage', 'amount', 'multiplier']:
            try:
                cleaned_row[col] = float(val)
            except ValueError:
                reject_reasons.append(f"Field '{col}' must be numeric")
                
        if col in ['quantity', 'stock_level', 'min_points', 'max_points']:
            try:
                cleaned_row[col] = int(float(val))
            except ValueError:
                reject_reasons.append(f"Field '{col}' must be integer")

        if col in ['transaction_date', 'registration_date', 'start_date', 'end_date']:
            try:
                pd.to_datetime(val)
            except Exception:
                reject_reasons.append(f"Field '{col}' must be a valid date")

    # 3. Business Rules
    for col in ['price', 'total_amount']:
        if col in cleaned_row and pd.notna(cleaned_row[col]) and isinstance(cleaned_row[col], (int, float)):
            if cleaned_row[col] < 0:
                reject_reasons.append(f"Field '{col}' must be >= 0")

    if 'quantity' in cleaned_row and pd.notna(cleaned_row['quantity']) and isinstance(cleaned_row['quantity'], (int, float)):
        if cleaned_row['quantity'] < 0:
            reject_reasons.append("Field 'quantity' must be >= 0")

    if 'stock_level' in cleaned_row and pd.notna(cleaned_row['stock_level']) and isinstance(cleaned_row['stock_level'], (int, float)):
         if cleaned_row['stock_level'] < 0:
            reject_reasons.append("Field 'stock_level' must be an integer >= 0")

    if 'discount_percentage' in cleaned_row and pd.notna(cleaned_row['discount_percentage']) and isinstance(cleaned_row['discount_percentage'], (int, float)):
        if not (0 <= cleaned_row['discount_percentage'] <= 100):
            reject_reasons.append("Field 'discount_percentage' must be between 0 and 100")

    if reject_reasons:
        return False, "; ".join(reject_reasons), row
    return True, "", cleaned_row

@handle_exceptions
def run_etl():
    os.makedirs(DATA_CLEAN, exist_ok=True)
    os.makedirs(DATA_REJECT, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Process each expected file
    for filename in FILES_EXPECTED:
        file_path = os.path.join(DATA_RAW, filename)
        table_name = filename.replace('.csv', '')
        rejected_table_name = f"{table_name}_rejected"
        
        if not os.path.exists(file_path):
            logger.warning(f"Expected file {filename} not found in {DATA_RAW}. Skipping.")
            continue
            
        try:
            df = pd.read_csv(file_path)
            
            # Clear core tables before inserting new data
            cursor.execute(f"DELETE FROM {table_name}")
            
            valid_rows = []
            rejected_rows = []
            
            for _, row in df.iterrows():
                is_valid, reason, c_row = validate_row(row, table_name)
                if is_valid:
                    valid_rows.append(c_row.to_dict())
                else:
                    rejected_rows.append({
                        "raw_data": json.dumps(row.to_dict()),
                        "reject_reason": reason,
                        "rejected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
            if valid_rows:
                valid_df = pd.DataFrame(valid_rows)
                # Export to data/cleaned
                valid_df.to_csv(os.path.join(DATA_CLEAN, filename), index=False)
                # Insert to db
                valid_df.to_sql(table_name, conn, if_exists='append', index=False)
                
            if rejected_rows:
                rej_df = pd.DataFrame(rejected_rows)
                # Export to data/rejected
                rej_file = os.path.join(DATA_REJECT, filename.replace('.csv', '_rejected.csv'))
                # append mode for rejected csv
                if os.path.exists(rej_file):
                    rej_df.to_csv(rej_file, mode='a', header=False, index=False)
                else:
                    rej_df.to_csv(rej_file, index=False)
                    
                # Insert to db
                rej_df.to_sql(rejected_table_name, conn, if_exists='append', index=False)
                
            logger.info(f"Processed {filename}: {len(valid_rows)} valid, {len(rejected_rows)} rejected.")
            
        except Exception as e:
            logger.error(f"Failed to process {filename}: {e}")
            raise ETLError(f"Failed to process {filename}: {e}")
            
    conn.commit()
    conn.close()
    logger.info("ETL pipeline complete.")
    print("ETL pipeline complete.")

if __name__ == "__main__":
    run_etl()
