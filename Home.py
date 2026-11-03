from datetime import date
from pathlib import Path
import sqlite3

import pandas as pd

import streamlit as st

st.set_page_config(page_title="Welcome to our Expense Tracker", page_icon="👋")

st.title("Welcome to our Expense Tracker Web App")
st.write("To interact with our app, access in in the sidebar pages.")
st.write("Get started now:")
st.page_link("pages/Expense_Tracker.py", label="**Expense Tracker**")

DB_PATH = Path(__file__).parent / "expense.db"

@st.cache_resource
def get_connection():

    connection = sqlite3.connect(
        DB_PATH, 
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection

connection = get_connection()

connection.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL CHECK (Amount > 0) 
)
""")

connection.commit()

