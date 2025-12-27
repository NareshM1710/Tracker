import streamlit as st
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

# File to store expenses
DATA_FILE = "expenses.json"

# Categories
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]

# Load expenses from file
def load_expenses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Save expenses to file
def save_expenses(expenses):
    with open(DATA_FILE, 'w') as f:
        json.dump(expenses, f, indent=2)

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = load_expenses()

# Page config
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="centered")

# Title
st.title("💰 Expense Tracker")

# Add Expense Section
st.subheader("Add Expense")

col1, col2 = st.columns(2)

with col1:
    amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0, format="%.2f")
    category = st.selectbox("Category", CATEGORIES)

with col2:
    date = st.date_input("Date", value=datetime.now())
    description = st.text_input("Description*", placeholder="e.g., Lunch at cafe")

if st.button("Add Expense", type="primary", use_container_width=True):
    if description.strip() == "":
        st.error("Description is mandatory!")
    elif amount <= 0:
        st.error("Amount must be greater than 0!")
    else:
        expense = {
            "date": date.strftime("%Y-%m-%d"),
            "amount": amount,
            "category": category,
            "description": description.strip()
        }
        st.session_state.expenses.append(expense)
        save_expenses(st.session_state.expenses)
        st.success("✅ Expense added!")
        st.rerun()

st.divider()

# Dashboard Section
st.subheader("📊 Dashboard")

# Calculate stats
today = datetime.now().date()
week_start = today - timedelta(days=today.weekday())
month_start = today.replace(day=1)

weekly_total = 0
monthly_total = 0
category_totals = defaultdict(float)

for expense in st.session_state.expenses:
    expense_date = datetime.strptime(expense['date'], "%Y-%m-%d").date()
    amount = expense['amount']
    
    if expense_date >= week_start:
        weekly_total += amount
    
    if expense_date >= month_start:
        monthly_total += amount
        category_totals[expense['category']] += amount

# Display stats
col1, col2 = st.columns(2)

with col1:
    st.metric("This Week", f"₹{weekly_total:,.2f}")

with col2:
    st.metric("This Month", f"₹{monthly_total:,.2f}")

# Top category this month
if category_totals:
    top_category = max(category_totals, key=category_totals.get)
    st.info(f"🏆 Top category this month: **{top_category}** (₹{category_totals[top_category]:,.2f})")

st.divider()

# View Expenses Section
if st.session_state.expenses:
    with st.expander("📋 View & Manage Expenses", expanded=False):
        # Sort expenses by date (newest first)
        sorted_expenses = sorted(st.session_state.expenses, key=lambda x: x['date'], reverse=True)
        
        for idx, expense in enumerate(sorted_expenses):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{expense['description']}**")
                st.caption(f"{expense['date']} • {expense['category']}")
            
            with col2:
                st.write(f"₹{expense['amount']:,.2f}")
            
            with col3:
                # Find original index for deletion
                original_idx = st.session_state.expenses.index(expense)
                if st.button("🗑️", key=f"delete_{original_idx}"):
                    st.session_state.expenses.pop(original_idx)
                    save_expenses(st.session_state.expenses)
                    st.rerun()
            
            st.divider()
        
        # Export button
        if st.button("📥 Export to CSV", use_container_width=True):
            import csv
            csv_file = "expenses_export.csv"
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['date', 'amount', 'category', 'description'])
                writer.writeheader()
                writer.writerows(st.session_state.expenses)
            st.success(f"✅ Exported to {csv_file}")
else:
    st.info("No expenses added yet. Start tracking your spending!")

# Footer
st.caption("---")
st.caption("💡 Tip: All data is saved locally in expenses.json")