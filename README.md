# Project 4: Product Research Tool

A Python program that scrapes book data from Books to Scrape (http://books.toscrape.com), stores the records in an SQLite database, and provides management tools via a CLI menu and a Flask web dashboard.

## Features

- **Web Scraper**: Extracts product title, price, availability status, and URL from Books to Scrape. Includes a 1-second delay between requests and handles connection errors.
- **SQLite Database**: Stores products in `products.db` with a unique constraint on URLs to prevent duplicate entries.
- **SQL CRUD Operations**: Full support for inserting, retrieving, updating, and deleting records.
- **Search & Filters**: Search products by name using SQL `LIKE`, or filter by price range using SQL `BETWEEN`.
- **Price Statistics**: Calculates cheapest, most expensive, and average product prices using SQL aggregation functions (`MIN`, `MAX`, `AVG`).
- **CSV Export**: Exports all stored products to a CSV file (`products.csv`).
- **Web Interface**: Simple Flask web application to view, search, and filter products from a browser.

## File Structure

- `scraper.py` - Scrapes product data from the website and saves it to SQLite.
- `database.py` - Database connection and SQL query functions.
- `main.py` - Interactive command-line menu.
- `app.py` - Flask web interface.
- `test_project.py` - Unit tests for database operations.
- `requirements.txt` - Python package dependencies.

## Installation

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Interactive CLI Menu
Run the main script:
```bash
python main.py
```
This opens an interactive menu with options to scrape data, search/filter, run CRUD operations, view statistics, export to CSV, or launch the web app.

### 2. Flask Web Dashboard
You can run the web app directly:
```bash
python app.py
```
Then open `http://127.0.0.1:5000` in your web browser.

### 3. Running Unit Tests
To run the automated tests:
```bash
python -m unittest test_project.py
```

## Database Schema

Table name: `products`

- `id` (INTEGER, Primary Key, Autoincrement)
- `name` (TEXT, Not Null)
- `price` (REAL, Not Null)
- `availability` (TEXT, Not Null)
- `url` (TEXT, Unique, Not Null)
