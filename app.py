"""
app.py
Flask web interface for viewing and filtering products.
"""

from flask import Flask, render_template_string, request
from database import (
    get_connection,
    init_db,
    get_all_products,
    get_cheapest_product,
    get_most_expensive_product,
    get_average_price
)

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Product Research Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background-color: #f7f9fa;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 960px;
            margin: 0 auto;
            background: #fff;
            padding: 24px;
            border-radius: 6px;
            border: 1px solid #e1e4e8;
        }
        h1 {
            margin-top: 0;
            color: #24292e;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin: 20px 0;
        }
        .stat-card {
            background: #f1f5f9;
            padding: 12px 16px;
            border-radius: 6px;
            border-left: 4px solid #2b6cb0;
        }
        .stat-card h4 {
            margin: 0 0 4px 0;
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
        }
        .stat-card p {
            margin: 0;
            font-size: 18px;
            font-weight: bold;
            color: #1e293b;
        }
        .filter-form {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .filter-form input {
            padding: 6px 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
        }
        .filter-form button, .filter-form a {
            padding: 6px 14px;
            font-size: 14px;
            border-radius: 4px;
            text-decoration: none;
            display: inline-block;
        }
        .btn-submit {
            background: #2b6cb0;
            color: white;
            border: none;
            cursor: pointer;
        }
        .btn-reset {
            background: #e2e8f0;
            color: #4a5568;
            line-height: 22px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            text-align: left;
            padding: 8px 10px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }
        th {
            background-color: #f8fafc;
            color: #475569;
        }
        .stock-tag {
            color: #166534;
            font-size: 12px;
            font-weight: 500;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Product Research Tool</h1>
    <p>Product records stored in SQLite database.</p>

    <div class="stats-grid">
        <div class="stat-card">
            <h4>Total Items</h4>
            <p>{{ total_count }}</p>
        </div>
        <div class="stat-card">
            <h4>Average Price</h4>
            <p>£{{ "%.2f"|format(avg_price) }}</p>
        </div>
        <div class="stat-card">
            <h4>Cheapest</h4>
            <p>£{{ "%.2f"|format(cheapest['price']) if cheapest else '0.00' }}</p>
        </div>
        <div class="stat-card">
            <h4>Most Expensive</h4>
            <p>£{{ "%.2f"|format(expensive['price']) if expensive else '0.00' }}</p>
        </div>
    </div>

    <form class="filter-form" method="GET" action="/">
        <input type="text" name="search" placeholder="Search name..." value="{{ search_query }}">
        <input type="number" step="0.01" name="min_price" placeholder="Min price" value="{{ min_price }}">
        <input type="number" step="0.01" name="max_price" placeholder="Max price" value="{{ max_price }}">
        <button class="btn-submit" type="submit">Filter</button>
        <a class="btn-reset" href="/">Reset</a>
    </form>

    <table>
        <thead>
            <tr>
                <th style="width: 40px;">ID</th>
                <th>Name</th>
                <th style="width: 90px;">Price</th>
                <th style="width: 110px;">Status</th>
                <th style="width: 60px;">Link</th>
            </tr>
        </thead>
        <tbody>
            {% for p in products %}
            <tr>
                <td>{{ p['id'] }}</td>
                <td>{{ p['name'] }}</td>
                <td>£{{ "%.2f"|format(p['price']) }}</td>
                <td><span class="stock-tag">{{ p['availability'] }}</span></td>
                <td><a href="{{ p['url'] }}" target="_blank">Link</a></td>
            </tr>
            {% else %}
            <tr>
                <td colspan="5" style="text-align: center; color: #888;">No products found.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
</body>
</html>
"""


@app.route("/")
def index():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    search_query = request.args.get("search", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search_query:
        query += " AND name LIKE ?"
        params.append(f"%{search_query}%")

    if min_price:
        try:
            query += " AND price >= ?"
            params.append(float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            query += " AND price <= ?"
            params.append(float(max_price))
        except ValueError:
            pass

    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    products = cursor.fetchall()

    avg_price = get_average_price(conn)
    cheapest = get_cheapest_product(conn)
    expensive = get_most_expensive_product(conn)
    total_count = len(products)

    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        products=products,
        total_count=total_count,
        avg_price=avg_price,
        cheapest=cheapest,
        expensive=expensive,
        search_query=search_query,
        min_price=min_price,
        max_price=max_price
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
