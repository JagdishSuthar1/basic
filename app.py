import streamlit as st
import pandas as pd
import mlflow
from sklearn.linear_model import LogisticRegression
import numpy as np


transaction_channel_map = df['transaction_channel'].value_counts(normalize=True).to_dict()
merchant_category_map = df['merchant_category'].value_counts(normalize=True).to_dict()
customer_region_map = df['customer_region'].value_counts(normalize=True).to_dict()
device_type_map = df['device_type'].value_counts(normalize=True).to_dict()

# Reverse maps for displaying original categories in Streamlit dropdowns
rev_transaction_channel_map = {v: k for k, v in transaction_channel_map.items()}
rev_merchant_category_map = {v: k for k, v in merchant_category_map.items()}
rev_customer_region_map = {v: k for k, v in customer_region_map.items()}
rev_device_type_map = {v: k for k, v in device_type_map.items()}

model = best_model

st.set_page_config(page_title="Fraud Prediction Dashboard", layout="wide")

st.title("💳 Banking Card Transaction Fraud Prediction")
st.markdown("Enter the transaction details to predict if it's a fraudulent activity.")

with st.sidebar:
    st.header("Transaction Details")

    transaction_amount_inr = st.number_input("Transaction Amount (INR) (Log Transformed):", min_value=0.0, value=2.0)
    account_age_months = st.slider("Account Age (Months):", min_value=1, max_value=180, value=50)
    available_balance_inr = st.number_input("Available Balance (INR) (Log Transformed):", min_value=0.0, value=10.0)
    monthly_income_inr = st.number_input("Monthly Income (INR) (Log Transformed):", min_value=0.0, value=10.0)
    credit_limit_inr = st.number_input("Credit Limit (INR) (Log Transformed):", min_value=0.0, value=11.0)
    credit_utilization_pct = st.slider("Credit Utilization (%):", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
    transactions_last_24h = st.number_input("Transactions Last 24h (Log Transformed):", min_value=0.0, value=1.0)
    avg_transaction_amount_30d_inr = st.number_input("Avg. Trans. Amount 30d (INR) (Log Transformed):", min_value=0.0, value=7.0)
    failed_logins_last_24h = st.number_input("Failed Logins Last 24h (Log Transformed):", min_value=0.0, value=0.0)
    distance_from_usual_location_km = st.number_input("Distance from Usual Location (KM) (Log Transformed):", min_value=0.0, value=3.0)
    international_transaction = st.selectbox("International Transaction:", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    card_present = st.selectbox("Card Present:", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    prior_disputes_12m = st.slider("Prior Disputes (Last 12 Months):", min_value=0, max_value=3, value=0)

    st.subheader("Categorical Features")
    selected_transaction_channel = st.selectbox("Transaction Channel:", list(transaction_channel_map.keys()))
    selected_merchant_category = st.selectbox("Merchant Category:", list(merchant_category_map.keys()))
    selected_customer_region = st.selectbox("Customer Region:", list(customer_region_map.keys()))
    selected_device_type = st.selectbox("Device Type:", list(device_type_map.keys()))

    st.subheader("Transaction Date/Time Components")
    year = st.number_input("Year:", min_value=2020, max_value=2030, value=2025)
    month = st.slider("Month:", min_value=1, max_value=12, value=7)
    day = st.slider("Day:", min_value=1, max_value=31, value=15)
    hour = st.slider("Hour:", min_value=0, max_value=23, value=12)
    minute = st.slider("Minute:", min_value=0, max_value=59, value=30)

if st.button("Predict Fraud"):
    transaction_channel_freq = transaction_channel_map.get(selected_transaction_channel, 0.0) # Default to 0 if not found
    merchant_category_freq = merchant_category_map.get(selected_merchant_category, 0.0)
    customer_region_freq = customer_region_map.get(selected_customer_region, 0.0)
    device_type_freq = device_type_map.get(selected_device_type, 0.0)

    input_data = pd.DataFrame([[
        transaction_amount_inr,
        transaction_channel_freq,
        merchant_category_freq,
        customer_region_freq,
        device_type_freq,
        account_age_months,
        available_balance_inr,
        monthly_income_inr,
        credit_limit_inr,
        credit_utilization_pct,
        transactions_last_24h,
        avg_transaction_amount_30d_inr,
        failed_logins_last_24h,
        distance_from_usual_location_km,
        international_transaction,
        card_present,
        prior_disputes_12m,
        year,
        month,
        day,
        hour,
        minute
    ]], columns=X_train.columns) # Use X_train columns to ensure correct order

    prediction = model.predict(input_data)
    prediction_proba = model.predict_proba(input_data)[:, 1]

    st.subheader("Prediction Result:")
    if prediction[0] == 1:
        st.error(f"**Fraudulent Transaction Detected!** (Probability: {prediction_proba[0]:.2f})")
    else:
        st.success(f"**Not Fraudulent.** (Probability: {prediction_proba[0]:.2f})")

    st.write("--- ")
    st.write("**Input Features:**")
    st.dataframe(input_data)