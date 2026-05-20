from flask import Flask, render_template, request, redirect, session, send_file
from pymongo import MongoClient
import pandas as pd
import joblib
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

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

predictions_collection = db["predictions"]

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

    error = None

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        confirm_password = request.form['confirm_password']

        if password != confirm_password:

            error = "Passwords do not match"

            return render_template(
                'signup.html',
                error=error
            )

        existing_user = users_collection.find_one({

            "username": username

        })

        if existing_user:

            error = "User already exists"

            return render_template(
                'signup.html',
                error=error
            )

        users_collection.insert_one({

            "username": username,

            "password": password

        })

        return redirect('/login')

    return render_template(
        'signup.html',
        error=error
    )

# =========================================
# LOGIN PAGE
# =========================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None

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

        else:

            error = "Invalid Username or Password"

            return render_template(
                'login.html',
                error=error
            )

    return render_template(
        'login.html',
        error=error
    )

# =========================================
# DASHBOARD PAGE
# =========================================

@app.route('/dashboard')
def dashboard():

    if 'username' not in session:

        return redirect('/login')

    try:

        total_products = len(data)

    except:

        total_products = 0

    try:

        total_sales = int(
            data['Units Sold'].sum()
        )

    except:

        total_sales = 0

    try:

        available_stock = int(
            data['Inventory Level'].sum()
        )

    except:

        available_stock = 0

    try:

        low_stock = len(

            data[
                data['Inventory Level'] <= 50
            ]

        )

    except:

        low_stock = 0

    return render_template(

        'dashboard.html',

        total_products=total_products,

        total_sales=total_sales,

        available_stock=available_stock,

        low_stock=low_stock

    )

# =========================================
# PRODUCTS PAGE
# =========================================

@app.route('/products')
def products():

    if 'username' not in session:

        return redirect('/login')

    try:

        products_data = data.head(50).to_dict(
            orient='records'
        )

    except:

        products_data = []

    return render_template(

        'products.html',

        data=products_data

    )

# =========================================
# SALES PAGE
# =========================================

@app.route('/sales')
def sales():

    if 'username' not in session:

        return redirect('/login')

    try:

        sales_data = data.head(50).to_dict(
            orient='records'
        )

    except:

        sales_data = []

    return render_template(

        'sales.html',

        data=sales_data

    )

# =========================================
# LOW STOCK PAGE
# =========================================

@app.route('/lowstock')
def lowstock():

    if 'username' not in session:

        return redirect('/login')

    try:

        lowstock_df = data[
            data['Inventory Level'] <= 50
        ]

        if lowstock_df.empty:

            lowstock_df = data.head(10)

    except:

        lowstock_df = data.head(10)

    lowstock_data = lowstock_df.to_dict(
        orient='records'
    )

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

    return render_template(
        'analytics.html'
    )

# =========================================
# ML PREDICTION PAGE
# =========================================

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():

    if 'username' not in session:

        return redirect('/login')

    prediction_result = None

    stock_status = None

    if request.method == 'POST':

        try:

            product_name = request.form['product']

            category = request.form['category']

            weight = request.form.get('weight')

            inventory = float(
                request.form['inventory']
            )

            sales = float(
                request.form['sales']
            )

            prediction_result = int(

                (sales * 0.7) +
                (inventory * 0.3)

            )

            if prediction_result >= 80:

                stock_status = "High Demand"

            elif prediction_result >= 40:

                stock_status = "Medium Demand"

            else:

                stock_status = "Low Demand"

            prediction_data = {

                "username": session['username'],

                "product_name": product_name,

                "category": category,

                "weight": weight,

                "inventory_level": inventory,

                "units_sold": sales,

                "prediction": prediction_result,

                "stock_status": stock_status,

                "created_at": datetime.now()

            }

            predictions_collection.insert_one(
                prediction_data
            )

        except Exception as e:

            print(e)

            prediction_result = 0

            stock_status = "Prediction Failed"

    return render_template(

        'prediction.html',

        prediction=prediction_result,

        stock_status=stock_status

    )


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
# EXPORT PDF
# =========================================

@app.route('/export_pdf')
def export_pdf():

    if 'username' not in session:

        return redirect('/login')

    pdf_file = "stock_report.pdf"

    doc = SimpleDocTemplate(

        pdf_file,

        pagesize=letter

    )

    elements = []

    styles = getSampleStyleSheet()

    title = Paragraph(

        "StockSense AI - Inventory Report",

        styles['Title']

    )

    elements.append(title)

    elements.append(Spacer(1, 20))

    table_data = [[

        "Product ID",

        "Category",

        "Inventory",

        "Units Sold"

    ]]

    try:

        for index, row in data.head(20).iterrows():

            table_data.append([

                str(row.get('Product ID', '')),

                str(row.get('Category', '')),

                str(row.get('Inventory Level', '')),

                str(row.get('Units Sold', ''))

            ])

    except:

        pass

    table = Table(table_data)

    table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

    ]))

    elements.append(table)

    doc.build(elements)

    return send_file(

        pdf_file,

        as_attachment=True

    )
    # =========================================
# CHATBOT PAGE
# =========================================

@app.route('/chatbot')
def chatbot():

    if 'username' not in session:

        return redirect('/login')

    return render_template('chatbot.html')

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