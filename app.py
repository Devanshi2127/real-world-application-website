from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # helps frontend talk to backend

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.before_first_request
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lost_items (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            location TEXT,
            image TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return "API Running"

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                   (data['name'], data['email'], data['password']))
    conn.commit()
    return jsonify({"msg":"Registered"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=? AND password=?",
                   (data['email'], data['password']))
    user = cursor.fetchone()

    if user:
        return jsonify({"msg":"Login Success", "user": dict(user)})
    else:
        return jsonify({"msg":"Invalid Details"}), 401

@app.route('/lost', methods=['GET','POST'])
def lost_items():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        d = request.json
        cursor.execute("INSERT INTO lost_items (title,description,location,image) VALUES (?,?,?,?)",
                       (d['title'],d['description'],d['location'], d.get('image','')))
        conn.commit()
        return jsonify({"msg":"Lost item added"}), 201

    cursor.execute("SELECT * FROM lost_items")
    items = cursor.fetchall()
    return jsonify([dict(i) for i in items])

if __name__ == "__main__":
    app.run(debug=True, port=5001)
