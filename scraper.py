"""
scraper.py
Scrapes book product data from Books to Scrape.
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from database import get_connection, insert_product, init_db, DEFAULT_DB

BASE_URL = "http://books.toscrape.com/catalogue/"


def clean_price(price_str):
    match = re.search(r"[\d.]+", price_str)
    if match:
        return float(match.group())
    return 0.0


def scrape_books(target_count=40, db_name=DEFAULT_DB):
    init_db(db_name)
    conn = get_connection(db_name)

    page_number = 1
    total_scraped = 0
    total_saved = 0
    total_duplicates = 0

    print(f"\nStarting scrape for books (target: {target_count})...")

    while total_scraped < target_count:
        page_url = f"{BASE_URL}page-{page_number}.html"
        print(f"Fetching page {page_number}: {page_url}")

        try:
            response = requests.get(page_url, timeout=10)
            if response.status_code == 404:
                print(f"Page {page_number} not found. Reached end of catalog.")
                break
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f"Request failed on page {page_number}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        book_pods = soup.find_all("article", class_="product_pod")

        if not book_pods:
            print("No items found on this page.")
            break

        for pod in book_pods:
            if total_scraped >= target_count:
                break

            # Book title
            title_tag = pod.find("h3").find("a")
            name = title_tag.get("title", title_tag.text).strip()

            # Product URL
            relative_url = title_tag.get("href", "")
            product_url = urljoin(BASE_URL, relative_url)

            # Price
            price_tag = pod.find("p", class_="price_color")
            raw_price = price_tag.text if price_tag else "0.0"
            price = clean_price(raw_price)

            # Availability
            avail_tag = pod.find("p", class_="instock availability")
            availability = " ".join(avail_tag.text.split()) if avail_tag else "Unknown"

            total_scraped += 1

            if insert_product(conn, name, price, availability, product_url):
                total_saved += 1
            else:
                total_duplicates += 1

        print(f"Processed page {page_number} ({len(book_pods)} books).")
        page_number += 1
        time.sleep(1)

    conn.close()

    print("\nScraping complete:")
    print(f"- Scanned: {total_scraped}")
    print(f"- Saved: {total_saved}")
    print(f"- Duplicates skipped: {total_duplicates}")
    print(f"- Database: {db_name}")

    return {
        "scraped": total_scraped,
        "saved": total_saved,
        "duplicates": total_duplicates
    }


if __name__ == "__main__":
    scrape_books(target_count=40)
