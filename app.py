from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
# Enable CORS so your HTML file can send data to this Python server
CORS(app)


# Function to setup the Database
def init_db():
    conn = sqlite3.connect('brand_magic_orders.db')
    cursor = conn.cursor()
    # Create the table with the NEW total_quantity column included
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            customer_phone TEXT,
            customer_address TEXT,
            items_bought TEXT,
            total_quantity INTEGER, 
            delivery_type TEXT,
            total_amount INTEGER,
            order_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# Initialize the database when the script starts
init_db()


# API Endpoint to receive the order data
@app.route('/api/save_order', methods=['POST'])
def save_order():
    data = request.json

    name = data.get('name')
    phone = data.get('phone')
    address = data.get('address')
    cart = data.get('cart', [])
    delivery_type = data.get('delivery_type')
    total_amount = data.get('total_amount')

    # 1. Calculate the total quantity of all items combined
    total_qty = sum(item['quantity'] for item in cart)

    # 2. Format the items so they are easy to read in the database (e.g., "2x Shot Glass, 1x Whiskey Glass")
    readable_items = ", ".join([f"{item['quantity']}x {item['name']}" for item in cart])

    try:
        # Save the order into the database
        conn = sqlite3.connect('brand_magic_orders.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO orders (customer_name, customer_phone, customer_address, items_bought, total_quantity, delivery_type, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, phone, address, readable_items, total_qty, delivery_type, total_amount))

        conn.commit()
        conn.close()

        print(f"✅ New Order Saved: {name} bought {total_qty} items (Total: ₹{total_amount})")
        return jsonify({"status": "success", "message": "Order saved to database!"}), 200

    except Exception as e:
        print(f"Error saving order: {e}")
        return jsonify({"status": "error", "message": "Failed to save order"}), 500


# Add this new endpoint to your script to view orders
@app.route('/admin/orders', methods=['GET'])
def view_orders():
    try:
        conn = sqlite3.connect('brand_magic_orders.db')
        conn.row_factory = sqlite3.Row  # This makes the data easy to access by column name
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY order_date DESC')
        rows = cursor.fetchall()

        # Convert database rows to a list of dictionaries
        orders = [dict(row) for row in rows]
        conn.close()

        return jsonify(orders)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Brand Magic Backend is running on http://127.0.0.1:8000")
    app.run(debug=True, port=8000)
