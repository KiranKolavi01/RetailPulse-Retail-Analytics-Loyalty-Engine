import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import bcrypt
import sqlite3
import pandas as pd
import os
import sys
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.utils.error_handler import handle_exceptions, logger

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
setup_db = load_module("setup_db", os.path.join(SRC_DIR, "01_setup_db.py"))
etl_pipeline = load_module("etl_pipeline", os.path.join(SRC_DIR, "02_etl_pipeline.py"))
loyalty_rfm = load_module("loyalty_rfm", os.path.join(SRC_DIR, "03_loyalty_rfm.py"))
predictive = load_module("predictive", os.path.join(SRC_DIR, "04_predictive.py"))
dashboard = load_module("dashboard", os.path.join(SRC_DIR, "05_dashboard.py"))

app = FastAPI(title="RetailPulse Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'retail.db')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# --- Models ---
class UserSignup(BaseModel):
    username: str
    email: str
    password: str

class UserSignin(BaseModel):
    username: str
    password: str

# --- DB Helper ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Authentication Endpoints ---
@app.post("/auth/signup")
def signup(user: UserSignup):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (user.username, user.email))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username or email already exists")
            
        hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (user.username, user.email, hashed_pw)
        )
        conn.commit()
        return {"status": "success", "username": user.username}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/auth/signin")
def signin(user: UserSignin):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (user.username,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        if bcrypt.checkpw(user.password.encode('utf-8'), row['password_hash']):
            return {"status": "success", "username": user.username}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    finally:
        conn.close()

# --- Pipeline Endpoints ---
# Temporary memory for status
pipeline_status = {
    "last_run": None,
    "status": "idle"
}

@app.post("/run-pipeline")
def run_pipeline():
    steps = []
    try:
        pipeline_status["status"] = "running"
        
        setup_db.setup_database()
        steps.append("setup_db")
        
        etl_pipeline.run_etl()
        steps.append("etl_pipeline")
        
        loyalty_rfm.run_loyalty_rfm()
        steps.append("loyalty_rfm")
        
        predictive.run_predictive_analytics()
        steps.append("predictive_analytics")
        
        dashboard.generate_dashboard()
        steps.append("dashboard")
        
        pipeline_status["last_run"] = datetime.now().isoformat()
        pipeline_status["status"] = "completed"
        return {"status": "success", "steps_completed": steps}
        
    except Exception as e:
        pipeline_status["status"] = f"failed at step {len(steps)+1}: {str(e)}"
        logger.error(f"Pipeline failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pipeline-status")
def get_pipeline_status():
    return pipeline_status

# --- Data Endpoints Helper ---
def fetch_table_data(table_name: str):
    conn = get_db_connection()
    try:
        # Check if table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Table not found")
            
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        # NaN Safety Rule
        df = df.where(pd.notnull(df), "")
        return df.to_dict(orient="records")
    finally:
        conn.close()

# --- Data Endpoints ---
@app.get("/stores")
def get_stores(): return fetch_table_data("stores")

@app.get("/products")
def get_products(): return fetch_table_data("products")

@app.get("/customers")
def get_customers(): return fetch_table_data("customer_details")

@app.get("/sales-header")
def get_sales_header(): return fetch_table_data("store_sales_header")

@app.get("/sales-line-items")
def get_sales_line_items(): return fetch_table_data("store_sales_line_items")

@app.get("/rfm-summary")
def get_rfm_summary(): return fetch_table_data("rfm_summary")

@app.get("/customer-predictions")
def get_customer_predictions(): return fetch_table_data("customer_predictions")

@app.get("/rejected/{table_name}")
def get_rejected_table(table_name: str):
    # Ensure getting a _rejected table
    if not table_name.endswith("_rejected"):
        raise HTTPException(status_code=400, detail="Only rejected tables can be accessed here")
    return fetch_table_data(table_name)

# --- Visualization Endpoints ---
@app.get("/visualizations/{filename}")
def get_visualization(filename: str):
    # Path traversal protection
    if not re.match(r"^[\w\-]+\.png$", filename):
        raise HTTPException(status_code=400, detail="Invalid filename format")
        
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Visualization file not found")
        
    with open(file_path, "rb") as image_file:
        content = image_file.read()
    return Response(content, media_type="image/png")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
