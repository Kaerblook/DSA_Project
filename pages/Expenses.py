from datetime import date

import streamlit as st
import pandas as pd

from services.methods import load_expenses

st.set_page_config("Expenses" )

expenses = load_expenses(date.min, date.max, "All categories")

def expense_table(exp: pd.DataFrame, curr_symbol: str = "₱") -> None:

    st.subheader("Expenses")


    if st.button("Refresh"):
        st.rerun()

    if exp.empty:
        st.info("No expenses found yet")
        return

    table_to_show = exp.drop(columns=["id"], errors="ignore").copy()

    if "Date" in table_to_show.columns:
        table_to_show["Date"] = (pd.to_datetime(table_to_show["Date"], errors="coerce").dt.strftime("%b %d, %Y"))

    if "Amount" in table_to_show.columns:
        num_amounts = pd.to_numeric(table_to_show["Amount"], errors="coerce")
        table_to_show["Amount"] = num_amounts.map(
            lambda amount: (
                f"{curr_symbol}{amount:,.2f}"
                if pd.notna(amount)
                else ""
            )
        )

    st.dataframe(table_to_show, use_container_width=True, hide_index=True)

    csv_data = (exp.drop(columns=["id"], errors="ignore").to_csv(index=False).encode("utf-8"))

    
    st.download_button("Download your expenses", data=csv_data, file_name="my_expenses.csv", mime="text/csv", key="dl_expenses_table")

expense_table(expenses)