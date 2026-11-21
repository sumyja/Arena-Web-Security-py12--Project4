"""
database.py
Database helper functions for SQLite storage and queries.
"""

import sqlite3
import csv
import os

DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products.db")


def get_connection(db_name=DEFAULT_DB):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_name=DEFAULT_DB):
    conn = get_connection(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            availability TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def insert_product(conn, name, price, availability, url):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO products (name, price, availability, url)
            VALUES (?, ?, ?, ?)
        """, (name, float(price), availability, url))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Ignore duplicate URLs
        return False


def get_all_products(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id ASC")
    return cursor.fetchall()


def get_product_by_id(conn, product_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    return cursor.fetchone()


def search_by_name(conn, keyword):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE name LIKE ? ORDER BY id ASC", (f"%{keyword}%",))
    return cursor.fetchall()


def filter_by_price(conn, min_price, max_price):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products 
        WHERE price BETWEEN ? AND ? 
        ORDER BY price ASC
    """, (min_price, max_price))
    return cursor.fetchall()


def get_cheapest_product(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY price ASC LIMIT 1")
    return cursor.fetchone()


def get_most_expensive_product(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY price DESC LIMIT 1")
    return cursor.fetchone()


def get_average_price(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(price) as avg_price FROM products")
    row = cursor.fetchone()
    if row and row["avg_price"] is not None:
        return round(row["avg_price"], 2)
    return 0.0


def update_product(conn, product_id, name, price, availability):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products 
        SET name = ?, price = ?, availability = ?
        WHERE id = ?
    """, (name, float(price), availability, product_id))
    conn.commit()
    return cursor.rowcount > 0


def delete_product(conn, product_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    return cursor.rowcount > 0


DEFAULT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products.csv")


def export_to_csv(conn, filename=DEFAULT_CSV):
    products = get_all_products(conn)
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Price", "Availability", "URL"])
        for p in products:
            writer.writerow([p["id"], p["name"], p["price"], p["availability"], p["url"]])
    return len(products)
