import pandas as pd
import sqlite3
import os
import sys

# Ensure error_handler is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from src.utils.error_handler import handle_exceptions, logger, AnalyticsError
except ImportError:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db', 'retail.db')

def calculate_promo_sensitivity(segment, frequency):
    if segment == "High Spender" or frequency >= 5:
        return "HIGH"
    elif segment == "At Risk" or frequency <= 2:
        return "LOW"
    else:
        return "MEDIUM"

@handle_exceptions
def run_predictive_analytics():
    conn = sqlite3.connect(DB_PATH)
    try:
        # Clear existing predictions
        conn.execute("DELETE FROM customer_predictions")
        conn.execute("DELETE FROM product_restock_predictions")
        
        try:
            rfm_df = pd.read_sql("SELECT * FROM rfm_summary", conn)
            sales_df = pd.read_sql("SELECT * FROM store_sales_header", conn)
            products_df = pd.read_sql("SELECT * FROM products", conn)
        except Exception as e:
            raise AnalyticsError(f"Failed to load core tables: {e}")
            
        if rfm_df.empty or sales_df.empty:
            logger.warning("Not enough data to run predictive analytics.")
            return
            
        sales_df['transaction_date'] = pd.to_datetime(sales_df['transaction_date'])
        current_date_max = sales_df['transaction_date'].max()
        
        # 1. Spend Forecasting: 3-month moving average
        # Calculate spend in the last 90 days
        cutoff_date = current_date_max - pd.Timedelta(days=90)
        recent_sales = sales_df[sales_df['transaction_date'] >= cutoff_date]
        
        # Monthly average over the last 3 months
        customer_monthly_avg = recent_sales.groupby('customer_id')['total_amount'].sum() / 3
        
        # 2. Promotion Sensitivity
        predictions = []
        for _, row in rfm_df.iterrows():
            cid = row['customer_id']
            freq = row['frequency']
            segment = row['segment']
            
            sensitivity = calculate_promo_sensitivity(segment, freq)
            predicted_spend = customer_monthly_avg.get(cid, 0.0)
            
            predictions.append({
                "customer_id": cid,
                "predicted_next_month_spend": round(predicted_spend, 2),
                "promotion_sensitivity": sensitivity
            })
            
        pred_df = pd.DataFrame(predictions)
        if not pred_df.empty:
            pred_df.to_sql('customer_predictions', conn, if_exists='append', index=False)
            
        # 3. Restock Predictions
        if not products_df.empty:
            restock_preds = []
            for _, row in products_df.iterrows():
                pid = row['product_id']
                stock = row['stock_level']
                
                # Assume a fixed restock logic: threshold of 20
                if pd.notna(stock):
                    needs_restock = 1 if int(stock) < 20 else 0
                else:
                    needs_restock = 1 # Restock if unknown
                    
                restock_preds.append({
                    "product_id": pid,
                    "stock_level": stock,
                    "is_restock_needed": needs_restock
                })
            
            restock_df = pd.DataFrame(restock_preds)
            restock_df.to_sql('product_restock_predictions', conn, if_exists='append', index=False)
            
        logger.info("Predictive analytics complete.")
        print("Predictive analytics complete.")
        
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    run_predictive_analytics()
