import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

# Backend API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Mini ERP Dashboard", page_icon="🏢", layout="wide")

# Theme
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    h1, h2, h3 {
        color: #1f2937;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Session State for Auth
if "token" not in st.session_state:
    st.session_state.token = None

def login(username, password):
    try:
        response = st.session_state.requests.post(f"{BACKEND_URL}/token/form", data={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state.token = response.json().get("access_token")
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")
    except Exception as e:
        st.error(f"Cannot connect to backend: {e}")

if st.session_state.token is None:
    st.session_state.requests = requests.Session()
    st.title("Welcome to Mini ERP")
    st.subheader("Login to access the system")
    with st.form("login_form"):
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="password123")
        submit = st.form_submit_button("Login")
        if submit:
            login(username, password)
    st.stop()

# Authenticated Application
st.session_state.requests.headers.update({"Authorization": f"Bearer {st.session_state.token}"})

st.sidebar.title("🏢 Mini ERP")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Customers", "Products", "Sales Orders"])

if st.sidebar.button("Logout"):
    st.session_state.token = None
    st.rerun()

def get_data(endpoint):
    res = st.session_state.requests.get(f"{BACKEND_URL}/api/{endpoint}")
    if res.status_code == 200:
        return res.json()
    st.error(f"Failed to fetch {endpoint}")
    return []

def post_data(endpoint, payload):
    res = st.session_state.requests.post(f"{BACKEND_URL}/api/{endpoint}", json=payload)
    if res.status_code == 200:
        st.success("Successfully added!")
        st.rerun()
    else:
        st.error(f"Error: {res.text}")

if menu == "Dashboard":
    st.title("📊 Sales Dashboard")
    data = get_data("analytics/dashboard")
    if data:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"${data.get('total_revenue', 0):,.2f}")
        col2.metric("Total Sales Orders", data.get("total_orders", 0))
        col3.metric("Total Customers", data.get("total_customers", 0))
        
        st.markdown("### Top Products Analysis")
        top_products = data.get("top_products", [])
        if top_products:
            df = pd.DataFrame(top_products)
            fig = px.bar(df, x="name", y="sold", color="name", title="Units Sold by Product")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data available yet to display top products.")

elif menu == "Customers":
    st.title("👥 Customer Management")
    with st.expander("➕ Add New Customer"):
        with st.form("customer_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            address = st.text_input("Address")
            if st.form_submit_button("Save Customer"):
                post_data("customers", {"name": name, "email": email, "phone": phone, "address": address})
    
    st.subheader("Customer List")
    customers = get_data("customers")
    if customers:
        df = pd.DataFrame(customers)
        st.dataframe(df[["id", "name", "email", "phone", "address"]], use_container_width=True)

elif menu == "Products":
    st.title("📦 Product & Inventory")
    with st.expander("➕ Add New Product"):
        with st.form("product_form"):
            name = st.text_input("Product Name")
            sku = st.text_input("SKU Code")
            price = st.number_input("Unit Price ($)", min_value=0.01)
            stock = st.number_input("Initial Stock Quantity", min_value=0, step=1)
            if st.form_submit_button("Save Product"):
                post_data("products", {"name": name, "sku": sku, "price": price, "stock_quantity": stock})
    
    st.subheader("Inventory List")
    products = get_data("products")
    if products:
        df = pd.DataFrame(products)
        st.dataframe(df[["id", "name", "sku", "price", "stock_quantity"]], use_container_width=True)

elif menu == "Sales Orders":
    st.title("🛒 Sales Orders")
    
    products_db = get_data("products")
    customers_db = get_data("customers")
    
    with st.expander("➕ Create Sales Order"):
        with st.form("sales_form"):
            if customers_db and products_db:
                customer_map = {c["name"]: c["id"] for c in customers_db}
                product_map = {p["name"]: p["id"] for p in products_db}
                selected_cust = st.selectbox("Select Customer", list(customer_map.keys()))
                selected_prod = st.selectbox("Select Product", list(product_map.keys()))
                qty = st.number_input("Quantity", min_value=1, step=1)
                
                if st.form_submit_button("Place Order"):
                    payload = {
                        "customer_id": customer_map[selected_cust],
                        "items": [{"product_id": product_map[selected_prod], "quantity": qty}]
                    }
                    post_data("sales", payload)
            else:
                st.warning("Please add customers and products before creating an order.")
                st.form_submit_button("Okay", disabled=True)
                
    st.subheader("Order History")
    orders = get_data("sales")
    if orders:
        formatted = []
        for o in orders:
            formatted.append({
                "Order ID": o["id"],
                "Customer ID": o["customer_id"],
                "Total Amount": f"${o.get('total_amount', 0):,.2f}",
                "Status": o["status"].capitalize(),
                "Date": o["created_at"][:10]
            })
        st.dataframe(pd.DataFrame(formatted), use_container_width=True)
