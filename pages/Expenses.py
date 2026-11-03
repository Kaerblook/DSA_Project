from datetime import date

import streamlit as st
import pandas as pd
import plotly.express as px

from pages.Expense_Tracker import CATEGORIES
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


def expense_chart(expenses: pd.DataFrame, curr_symbol: str = "₱") -> None:

    st.subheader("Spending Pie Chart")

    req_columns = {"Name", "Date", "Category", "Amount"}
    missing_columns = req_columns.difference(expenses.columns)
    if missing_columns:
        st.error("Can't create the chart, missing a column" + ", ".join(sorted(missing_columns)))
        return

    chart_data = expenses.copy()
    chart_data["Date"] = pd.to_datetime(chart_data["Date"], errors="coerce")
    chart_data["Amount"] = pd.to_numeric(chart_data["Amount"], errors="coerce")

    chart_data = chart_data.dropna(subset=["Amount"])
    chart_data = chart_data.loc[chart_data["Amount"] > 0].copy()

    if chart_data.empty:
        st.info("No valid expense to display")
        return

    highest_expense = chart_data.loc[chart_data["Amount"].idxmax()]

    highest_name = str(highest_expense["Name"])
    highest_amount = float(highest_expense["Amount"])
    highest_date = highest_expense["Date"]
    highest_category = highest_expense["Category"]
    date_text = (highest_date.strftime("%b %d, %Y") if pd.notna(highest_date) else "Date unavailable")

    st.markdown("**Highest expense:***")
    st.write(
        f"{highest_name} ({highest_category}) ---"
        f"{curr_symbol}{highest_amount:,.2f} on {date_text}"
    )

    if "id" in chart_data.columns:
        chart_data["Chart label"] = chart_data.apply(
            lambda row: (
                f"{row['Name']}  {row['Category']}"
                f"{row['Date'].strftime('%b %d') if pd.notna(row['Date']) else 'No Date'}"
                f" #{row['id']}"
            ),
            axis=1,
        )
    else:
        chart_data["Chart label"] = chart_data.apply(
            lambda row:(
                f"{row['Name']}  {row['Category']}"
                f"{row['Date'].strftime('%b %d') if pd.notna(row['Date']) else 'No Date'}"
            ),
            axis=1   
        )

    pie_chart = px.pie(
        chart_data, names="Chart label", values="Amount", hole=0,
    )
    pie_chart.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            f"<b>%{{label}}</b></br>"
            f"Amount: {curr_symbol}%{{value:,.2f}}<br>"
            "Share: %{percent}<extra></extra>"
        ),
    )
    pie_chart.update_layout(
        legend_title_text="Individual expenses",
        margin=dict(t=20, b=20, l=10, r=10),
    )

    st.plotly_chart(
        pie_chart,
        use_container_width=True,
        key="pie_expense_chart",
    )

expense_table(expenses)

st.divider()

sel_categories = st.selectbox("Filter Category", ["All categories"] + CATEGORIES,)

exp_pie = load_expenses(date.min, date.max, sel_categories)

expense_chart(exp_pie)

