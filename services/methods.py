from datetime import date
import pandas as pd  # type: ignore[import-untyped]

from Home import connection 

def add_expense(name: str, date: date, category: str, amount: float):

    connection.execute("""
    INSERT INTO expenses (name, date, category, amount)
    VALUES (?, ?, ?, ?)
    """, 
    (name.lstrip(), date.isoformat(), category, amount))

    connection.commit()

def load_expenses(start_date: date, end_date: date, category: str):

    sql = """
        SELECT id, name AS Name, date AS Date, category AS Category, amount AS Amount
        FROM expenses WHERE date BETWEEN ? AND ?
"""

    parameters = [
        start_date.isoformat(),
        end_date.isoformat()
    ]

    if category != "All categories":
        sql += " AND category = ?"
        parameters.append(category)

    return pd.read_sql_query(sql, connection, params=parameters)

def delete_expense(exp_id: int):
    connection.execute("DELETE FROM expenses WHERE id = ?", (int(exp_id),))
    connection.commit()