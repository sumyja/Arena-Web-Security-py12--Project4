"""
main.py
CLI interface for the product research tool.
"""

from database import (
    get_connection,
    init_db,
    get_all_products,
    get_product_by_id,
    insert_product,
    update_product,
    delete_product,
    search_by_name,
    filter_by_price,
    get_cheapest_product,
    get_most_expensive_product,
    get_average_price,
    export_to_csv,
    DEFAULT_CSV
)
from scraper import scrape_books


def print_table(products):
    if not products:
        print("\nNo products found.")
        return

    print("\n" + "-" * 80)
    print(f"{'ID':<4} | {'Name':<42} | {'Price':<10} | {'Status':<15}")
    print("-" * 80)
    for p in products:
        short_name = p["name"][:39] + "..." if len(p["name"]) > 42 else p["name"]
        print(f"{p['id']:<4} | {short_name:<42} | £{p['price']:<9.2f} | {p['availability']:<15}")
    print("-" * 80)
    print(f"Total: {len(products)} products")


def menu_scrape():
    print("\n--- Scrape Products ---")
    raw = input("How many products to scrape? (min 30, default 40): ").strip()
    count = int(raw) if raw.isdigit() and int(raw) >= 30 else 40
    scrape_books(target_count=count)


def menu_view_all():
    conn = get_connection()
    products = get_all_products(conn)
    print_table(products)
    conn.close()


def menu_search():
    keyword = input("\nEnter search keyword: ").strip()
    if not keyword:
        print("Keyword cannot be empty.")
        return
    conn = get_connection()
    results = search_by_name(conn, keyword)
    print_table(results)
    conn.close()


def menu_filter_price():
    try:
        min_p = float(input("\nEnter minimum price: ").strip())
        max_p = float(input("Enter maximum price: ").strip())
        if min_p > max_p:
            print("Minimum price cannot exceed maximum price.")
            return
        conn = get_connection()
        results = filter_by_price(conn, min_p, max_p)
        print_table(results)
        conn.close()
    except ValueError:
        print("Please enter valid numeric prices.")


def menu_statistics():
    conn = get_connection()
    cheapest = get_cheapest_product(conn)
    expensive = get_most_expensive_product(conn)
    avg_price = get_average_price(conn)
    conn.close()

    print("\n" + "=" * 45)
    print("              Price Statistics")
    print("=" * 45)

    if not cheapest:
        print("Database is currently empty.")
        return

    print(f"Cheapest:")
    print(f"  {cheapest['name']}")
    print(f"  £{cheapest['price']:.2f} ({cheapest['availability']})")

    if expensive:
        print(f"\nMost Expensive:")
        print(f"  {expensive['name']}")
        print(f"  £{expensive['price']:.2f} ({expensive['availability']})")

    print(f"\nAverage Price: £{avg_price:.2f}")
    print("=" * 45)


def menu_add_product():
    print("\n--- Add Product ---")
    name = input("Product name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    try:
        price = float(input("Price (e.g. 19.99): ").strip())
    except ValueError:
        print("Invalid price format.")
        return

    availability = input("Availability (default 'In stock'): ").strip()
    if not availability:
        availability = "In stock"

    url = input("Product URL: ").strip()
    if not url:
        url = f"https://books.toscrape.com/catalogue/custom-{name.lower().replace(' ', '-')}"

    conn = get_connection()
    if insert_product(conn, name, price, availability, url):
        print(f"Added product: {name}")
    else:
        print("A product with this URL already exists.")
    conn.close()


def menu_update_product():
    print("\n--- Update Product ---")
    try:
        p_id = int(input("Enter product ID: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    conn = get_connection()
    prod = get_product_by_id(conn, p_id)
    if not prod:
        print(f"No product with ID {p_id}.")
        conn.close()
        return

    print(f"Current: {prod['name']} | £{prod['price']:.2f} | {prod['availability']}")

    new_name = input(f"New name (leave blank to keep): ").strip() or prod['name']
    raw_price = input(f"New price (leave blank to keep): ").strip()
    try:
        new_price = float(raw_price) if raw_price else prod['price']
    except ValueError:
        print("Invalid price, keeping current.")
        new_price = prod['price']

    new_avail = input(f"New availability (leave blank to keep): ").strip() or prod['availability']

    update_product(conn, p_id, new_name, new_price, new_avail)
    conn.close()
    print("Product updated.")


def menu_delete_product():
    print("\n--- Delete Product ---")
    try:
        p_id = int(input("Enter product ID to delete: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    conn = get_connection()
    prod = get_product_by_id(conn, p_id)
    if not prod:
        print(f"No product with ID {p_id}.")
        conn.close()
        return

    confirm = input(f"Delete '{prod['name']}'? (y/n): ").strip().lower()
    if confirm in ("y", "yes"):
        delete_product(conn, p_id)
        print("Product deleted.")
    else:
        print("Cancelled.")
    conn.close()


def menu_export_csv():
    conn = get_connection()
    total = export_to_csv(conn, DEFAULT_CSV)
    conn.close()
    print(f"\nExported {total} records to {DEFAULT_CSV}")


def menu_run_flask():
    print("\nStarting Flask web app on http://127.0.0.1:5000 ...")
    print("Press Ctrl+C to stop.\n")
    try:
        from app import app
        app.run(debug=False, port=5000)
    except Exception as e:
        print(f"Error launching web app: {e}")


def main():
    init_db()

    while True:
        print("\n" + "=" * 45)
        print("           Product Research Tool")
        print("=" * 45)
        print("  1. Scrape Products")
        print("  2. View All Products")
        print("  3. Search Products by Name")
        print("  4. Filter Products by Price Range")
        print("  5. View Price Statistics")
        print("  6. Add Product")
        print("  7. Update Product")
        print("  8. Delete Product")
        print("  9. Export to CSV")
        print(" 10. Launch Web Interface")
        print("  0. Exit")
        print("=" * 45)

        choice = input("Select an option (0-10): ").strip()

        if choice == "1":
            menu_scrape()
        elif choice == "2":
            menu_view_all()
        elif choice == "3":
            menu_search()
        elif choice == "4":
            menu_filter_price()
        elif choice == "5":
            menu_statistics()
        elif choice == "6":
            menu_add_product()
        elif choice == "7":
            menu_update_product()
        elif choice == "8":
            menu_delete_product()
        elif choice == "9":
            menu_export_csv()
        elif choice == "10":
            menu_run_flask()
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print("Invalid selection, please try again.")


if __name__ == "__main__":
    main()
