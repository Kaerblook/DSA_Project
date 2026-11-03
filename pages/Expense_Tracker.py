import pandas as pd
import streamlit as st
import plotly.express as px

from services.methods import add_expense, load_expenses, delete_expense

from utils.utilities import money, CURRENCY_SYMBOL


import time

st.set_page_config(page_title="Expense Tracker", page_icon="")

CATEGORIES = [
    "Food & Drinks",
    "Groceries",
    "Transportation",
    "Bills & Utilities",
    "Shopping",
    "Health",
    "Education",
    "Entertainment",
    "Personal Care",
    "Other",
]

with st.form("add_expense", clear_on_submit=True):

    st.title("Add Expenses")

    name = st.text_input(label="Name of the Expense:")
    date = st.date_input("Date")
    category = st.selectbox("Expense Category", CATEGORIES)
    amount = st.number_input("Amount", min_value=0.01)

    submit = st.form_submit_button("Add", use_container_width=True)

    if submit:
        if amount < 0:
            st.error("Please input an amount greater than or equal to 0")
        else:
            add_expense(name, date, category, amount)   
            st.success("Expenses has been added!")
            time.sleep(1.8)
            st.rerun()

st.divider()

st.header("Filter Expenses")

today = date.today()
fd_month = today.replace(day=1) # first day of the month
sel_dates = st.date_input(
    "Date range",
    value=(fd_month, today),
    key="date_filter",
)

if isinstance(sel_dates, (tuple, list)):
    if len(sel_dates) == 2:
        start_date, end_date = sel_dates
    elif len(sel_dates) == 1:
        start_date = end_date = sel_dates[0]
    else:
        start_date, end_date = fd_month, today
else:
    start_date = end_date = sel_dates


if start_date > end_date:
    start_date, end_date = end_date, start_date

sel_categories = st.selectbox("Filter Category", ["All categories"] + CATEGORIES,)

expenses = load_expenses(start_date, end_date, sel_categories)


if expenses.empty:
    st.info("No expenses added yet, add an expense to see the result or choose another date range")
else:

    expenses["Date"] = pd.to_datetime(expenses["Date"])

    total_spent = float(expenses["Amount"].sum())
    trans_count = len(expenses)
    avg_expenses = total_spent / trans_count

    col1, col2, col3 = st.columns(3)
    col1.metric("Total spent", money(total_spent)) 
    col2.metric("Transaction", f"{trans_count:,}")
    col3.metric("Average Expense", money(avg_expenses))

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Spending by category")
        cat_totals = (expenses.groupby("Category", as_index=False)["Amount"]
                      .sum().
                      sort_values("Amount", ascending=False))
        
        cat_chart = px.bar(cat_totals, x="Category", y="Amount", labels={"Amount": f"Amount ({CURRENCY_SYMBOL})"})

        cat_chart.update_layout(xaxis_title="", yaxis_title="Amount")
        st.plotly_chart(cat_chart, use_container_width=True)

    with chart_col2:
        st.subheader("Spending over time")

        daily_totals = (expenses.groupby("Date", as_index=False)["Amount"].sum().sort_values("Date"))

        daily_chart = px.line(daily_totals, x="Date", y="Amount", markers=True, labels={"Amount": f"Amount ({CURRENCY_SYMBOL})"})

        daily_chart.update_layout(xaxis_title="Date", yaxis_title="Amount")
        st.plotly_chart(daily_chart, use_container_width=True)

    with st.sidebar:  # noqa: SIM117
        with st.expander("Delete an Expense"):
                st.warning("This will permanently delete your transaction")

                def trans_label(exp_id):
                    row = expenses.loc[expenses["id"] == exp_id].iloc[0]
                    return (
                        f"{row['Name']} "
                        f"{row['Date'].strftime('%b %d %Y')} "
                    )

                sel_exp_id = st.selectbox('Choose what to delete', options=expenses["id"].tolist(), format_func=trans_label)

                confirmation = st.checkbox("I understand that deleting a transaction is permanent.")

                if st.button("Delete selected transaction", type="secondary"):
                    if confirmation:
                        delete_expense(sel_exp_id)
                        st.success("Successfully deleted.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Please confirm in order to delete the transaction")

                


