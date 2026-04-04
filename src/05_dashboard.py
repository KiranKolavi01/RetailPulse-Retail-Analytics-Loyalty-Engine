import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os
import sys

# Ensure error_handler is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from src.utils.error_handler import handle_exceptions, logger, AnalyticsError
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'db', 'retail.db')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

@handle_exceptions
def generate_dashboard():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    try:
        sales_df = pd.read_sql("SELECT * FROM store_sales_header", conn)
        rfm_df = pd.read_sql("SELECT * FROM rfm_summary", conn)
        line_items_df = pd.read_sql("SELECT * FROM store_sales_line_items", conn)
        products_df = pd.read_sql("SELECT * FROM products", conn)
        
        if sales_df.empty or rfm_df.empty or line_items_df.empty or products_df.empty:
            logger.warning("Insufficient data to generate dashboard visualizations.")
            return

        # Prepare a 2x2 grid for the combined dashboard
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('RetailPulse Dashboard', fontsize=16)
        
        # 1. Sales Trends (Daily Total Amount)
        sales_df['transaction_date'] = pd.to_datetime(sales_df['transaction_date'])
        daily_sales = sales_df.groupby(sales_df['transaction_date'].dt.date)['total_amount'].sum()
        
        ax1 = axes[0, 0]
        daily_sales.plot(kind='line', ax=ax1, color='blue', marker='o')
        ax1.set_title('Sales Trends')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Total Amount')
        
        # Save individual chart1
        fig1, ax_ind1 = plt.subplots(figsize=(8, 5))
        daily_sales.plot(kind='line', ax=ax_ind1, color='blue', marker='o')
        ax_ind1.set_title('Sales Trends')
        ax_ind1.set_xlabel('Date')
        ax_ind1.set_ylabel('Total Amount')
        fig1.savefig(os.path.join(OUTPUT_DIR, 'chart1_sales_trends.png'))
        plt.close(fig1)

        # 2. Customer Loyalty Distribution
        loyalty_counts = rfm_df['loyalty_tier'].value_counts()
        
        ax2 = axes[0, 1]
        loyalty_counts.plot(kind='pie', ax=ax2, autopct='%1.1f%%', startangle=90, colors=['gold', 'silver', 'cd853f'])
        ax2.set_title('Customer Loyalty Distribution')
        ax2.set_ylabel('')
        
        # Save individual chart2
        fig2, ax_ind2 = plt.subplots(figsize=(8, 5))
        loyalty_counts.plot(kind='pie', ax=ax_ind2, autopct='%1.1f%%', startangle=90, colors=['gold', 'silver', 'cd853f'])
        ax_ind2.set_title('Customer Loyalty Distribution')
        ax_ind2.set_ylabel('')
        fig2.savefig(os.path.join(OUTPUT_DIR, 'chart2_loyalty_distribution.png'))
        plt.close(fig2)

        # 3. At-risk customer alerts
        segment_counts = rfm_df['segment'].value_counts()
        
        ax3 = axes[1, 0]
        segment_counts.plot(kind='bar', ax=ax3, color=['grey', 'red', 'green'])
        ax3.set_title('Customer Segments (At-Risk Alerts)')
        ax3.set_xlabel('Segment')
        ax3.set_ylabel('Count')
        ax3.tick_params(axis='x', rotation=45)
        
        # Save individual chart3
        fig3, ax_ind3 = plt.subplots(figsize=(8, 5))
        segment_counts.plot(kind='bar', ax=ax_ind3, color=['grey', 'red', 'green'])
        ax_ind3.set_title('Customer Segments (At-Risk Alerts)')
        ax_ind3.set_xlabel('Segment')
        ax_ind3.set_ylabel('Count')
        ax_ind3.tick_params(axis='x', rotation=45)
        fig3.tight_layout()
        fig3.savefig(os.path.join(OUTPUT_DIR, 'chart3_customer_segments.png'))
        plt.close(fig3)

        # 4. Top products analysis
        merged_items = pd.merge(line_items_df, products_df, on='product_id', how='left')
        merged_items['revenue'] = merged_items['quantity'] * merged_items['price_x'] # price from line item
        top_products = merged_items.groupby('product_name')['revenue'].sum().sort_values(ascending=False).head(5)
        
        ax4 = axes[1, 1]
        top_products.plot(kind='bar', ax=ax4, color='purple')
        ax4.set_title('Top 5 Products by Revenue')
        ax4.set_xlabel('Product Name')
        ax4.set_ylabel('Revenue')
        ax4.tick_params(axis='x', rotation=45)
        
        # Save individual chart4
        fig4, ax_ind4 = plt.subplots(figsize=(8, 5))
        top_products.plot(kind='bar', ax=ax_ind4, color='purple')
        ax_ind4.set_title('Top 5 Products by Revenue')
        ax_ind4.set_xlabel('Product Name')
        ax_ind4.set_ylabel('Revenue')
        ax_ind4.tick_params(axis='x', rotation=45)
        fig4.tight_layout()
        fig4.savefig(os.path.join(OUTPUT_DIR, 'chart4_top_products.png'))
        plt.close(fig4)

        # Save combined dashboard
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.savefig(os.path.join(OUTPUT_DIR, 'dashboard.png'))
        plt.close(fig)
        
        logger.info("Dashboard visualizations generated in output/ directory.")
        print("Dashboard visualizations generated in output/ directory.")
        
    except Exception as e:
        raise AnalyticsError(f"Failed to generate dashboard: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    generate_dashboard()
