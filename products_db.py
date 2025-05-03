import sqlite3
import os

def get_db_path():
    db_dir = os.path.expanduser("~/Documents/invoices")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "products.db")

def init_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_product(name, description, price):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO products (name, description, price)
        VALUES (?, ?, ?)
    ''', (name, description, price))
    conn.commit()
    product_id = c.lastrowid
    conn.close()
    return product_id

def get_products():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT product_id, name, description, price FROM products')
    products = c.fetchall()
    conn.close()
    return products

def get_product(product_id):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT product_id, name, description, price FROM products WHERE product_id=?', (product_id,))
    product = c.fetchone()
    conn.close()
    return product

def update_product(product_id, name, description, price):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        UPDATE products SET name=?, description=?, price=? WHERE product_id=?
    ''', (name, description, price, product_id))
    conn.commit()
    conn.close()
