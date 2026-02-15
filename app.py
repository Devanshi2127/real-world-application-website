from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = "database.db"

# -------------------------
# Database Connection
# -------------------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# Initialize Database
# -------------------------
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Items table (Lost + Found)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            location TEXT,
            contact TEXT,
            type TEXT
        )
    ''')

    conn.commit()
    conn.close()


# -------------------------
# Home Route
# -------------------------
@app.route('/')
def home():
    return "Lost & Found Backend Running 🚀"


# -------------------------
# Register Route
# -------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (data['name'], data['email'], data['password'])
        )
        conn.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already exists!"}), 400
    finally:
        conn.close()


# -------------------------
# Login Route
# -------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (data['email'], data['password'])
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "message": "Login successful!",
            "user": dict(user)
        })
    else:
        return jsonify({"message": "Invalid email or password"}), 401


# -------------------------
# Add Item (Lost or Found)
# -------------------------
@app.route('/items', methods=['POST'])
def add_item():
    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO items (title, description, location, contact, type) VALUES (?, ?, ?, ?, ?)",
        (data['title'], data['description'], data['location'], data['contact'], data['type'])
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Item added successfully!"}), 201


# -------------------------
# Get All Items
# -------------------------
@app.route('/items', methods=['GET'])
def get_items():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()

    return jsonify([dict(item) for item in items])


# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    init_db()  # Initialize DB
    app.run(host="0.0.0.0", port=5001, debug=True)
