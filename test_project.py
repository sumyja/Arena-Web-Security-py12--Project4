"""
test_project.py
Unit tests for database and queries.
"""

import os
import unittest
from database import (
    get_connection,
    init_db,
    insert_product,
    get_all_products,
    get_product_by_id,
    update_product,
    delete_product,
    search_by_name,
    filter_by_price,
    get_cheapest_product,
    get_most_expensive_product,
    get_average_price,
    export_to_csv
)

TEST_DB = "test_products.db"
TEST_CSV = "test_products.csv"


class TestProductResearchTool(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        init_db(TEST_DB)
        self.conn = get_connection(TEST_DB)

        insert_product(self.conn, "Python Basics", 25.00, "In stock", "http://example.com/p1")
        insert_product(self.conn, "Advanced Python", 45.00, "In stock", "http://example.com/p2")
        insert_product(self.conn, "Data Science Handbook", 50.00, "In stock", "http://example.com/p3")

    def tearDown(self):
        self.conn.close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        if os.path.exists(TEST_CSV):
            os.remove(TEST_CSV)

    def test_insert_and_retrieve(self):
        products = get_all_products(self.conn)
        self.assertEqual(len(products), 3)
        self.assertEqual(products[0]["name"], "Python Basics")

    def test_duplicate_prevention(self):
        result = insert_product(self.conn, "Duplicate Book", 30.00, "In stock", "http://example.com/p1")
        self.assertFalse(result)
        products = get_all_products(self.conn)
        self.assertEqual(len(products), 3)

    def test_search_by_name(self):
        matches = search_by_name(self.conn, "Python")
        self.assertEqual(len(matches), 2)

    def test_filter_by_price(self):
        matches = filter_by_price(self.conn, 20.00, 30.00)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "Python Basics")

    def test_sql_statistics(self):
        cheapest = get_cheapest_product(self.conn)
        expensive = get_most_expensive_product(self.conn)
        avg = get_average_price(self.conn)

        self.assertEqual(cheapest["price"], 25.00)
        self.assertEqual(expensive["price"], 50.00)
        self.assertEqual(avg, 40.0)

    def test_update_product(self):
        p = get_all_products(self.conn)[0]
        update_product(self.conn, p["id"], "Python Basics 2nd Edition", 29.99, "Out of stock")

        updated = get_product_by_id(self.conn, p["id"])
        self.assertEqual(updated["name"], "Python Basics 2nd Edition")
        self.assertEqual(updated["price"], 29.99)
        self.assertEqual(updated["availability"], "Out of stock")

    def test_delete_product(self):
        p = get_all_products(self.conn)[0]
        delete_product(self.conn, p["id"])

        products = get_all_products(self.conn)
        self.assertEqual(len(products), 2)
        self.assertIsNone(get_product_by_id(self.conn, p["id"]))

    def test_csv_export(self):
        count = export_to_csv(self.conn, TEST_CSV)
        self.assertEqual(count, 3)
        self.assertTrue(os.path.exists(TEST_CSV))


if __name__ == "__main__":
    unittest.main()
