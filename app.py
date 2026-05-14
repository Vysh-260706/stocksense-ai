from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
import pandas as pd
import joblib

# =========================================
# FLASK APP
# =========================================

app = Flask(__name__)
app.secret_key = "StockSense_secret"

# =========================================
# MONGODB CONNECTION
# =========================================

MONGO_URI = "mongodb+srv://vyshnavi06:stocksense123@stocksense.8llxisw.mongodb.net/StockSense_db?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)

db = client["StockSense_db"]
users_collection = db["users"]

# =========================================
# LOAD DATASET
# =========================================

DATASET_PATH = "dataset/retail_store_inventory.csv"

try:
    data = pd.read_csv(DATASET_PATH)
except:
    data = pd.DataFrame()

# =========================================
# LOAD MODEL
# =========================================

try:
    model = joblib.load("inventory_model.pkl")
except:
    model = None

# =========================================
# HOME PAGE
# =========================================

@app.route('/')
def home():
    return render_template('home.html')

# =========================================
# SIGNUP PAGE
# =========================================

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Password Match Check
        if password != confirm_password:
            return "Passwords do not match"

        # Existing User Check
        existing_user = users_collection.find_one({
            "username": username
        })

        if existing_user:
            return "User already exists"

        # Insert New User
        users_collection.insert_one({
            "username": username,
            "password": password
        })

        return redirect('/login')

    return render_template('signup.html')

# =========================================
# LOGIN PAGE
# =========================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({
            "username": username,
            "password": password
        })

        if user:
            session['username'] = username
            return redirect('/dashboard')

        return "Invalid Username or Password"

    return render_template('login.html')

# =========================================
# DASHBOARD PAGE
# =========================================

@app.route('/dashboard')
def dashboard():

    if 'username' not in session:
        return redirect('/login')

    total_products = len(data)

    total_sales = 0

    try:
        total_sales = int(data['Units Sold'].sum())
    except:
        total_sales = 0

    low_stock = 0

    try:
        low_stock = len(data[data['Inventory Level'] < 20])
    except:
        low_stock = 0

    return render_template(
        'dashboard.html',
        total_products=total_products,
        total_sales=total_sales,
        low_stock=low_stock
    )

# =========================================
# PRODUCTS PAGE
# =========================================

# =========================================
# PRODUCTS PAGE
# =========================================

@app.route('/products')
def products():

    if 'username' not in session:
        return redirect('/login')

    products_data = data.head(50).to_dict(orient='records')

    return render_template(
        'products.html',
        data=products_data
    )

# =========================================
# SALES PAGE
# =========================================

# =========================================
# SALES PAGE
# =========================================

@app.route('/sales')
def sales():

    if 'username' not in session:
        return redirect('/login')

    sales_data = data.head(50).to_dict(orient='records')

    return render_template(
        'sales.html',
        data=sales_data
    )

# =========================================
# LOW STOCK PAGE
# =========================================

# =========================================
# LOW STOCK PAGE
# =========================================

@app.route('/lowstock')
def lowstock():

    if 'username' not in session:
        return redirect('/login')

    lowstock_data = data.head(50).to_dict(orient='records')

    return render_template(
        'lowstock.html',
        data=lowstock_data
    )

# =========================================
# ANALYTICS PAGE
# =========================================

@app.route('/analytics')
def analytics():

    if 'username' not in session:
        return redirect('/login')

    return render_template('analytics.html')

# =========================================
# PROFILE PAGE
# =========================================

@app.route('/profile')
def profile():

    if 'username' not in session:
        return redirect('/login')

    return render_template(
        'profile.html',
        username=session['username']
    )

# =========================================
# LOGOUT
# =========================================

@app.route('/logout')
def logout():

    session.pop('username', None)

    return redirect('/login')

# =========================================
# RUN APP
# =========================================

if __name__ == "__main__":
    app.run(debug=True)