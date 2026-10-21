import unittest
from app import app


class ProductsBlueprintTestCase(unittest.TestCase):

    def setUp(self):
        """Налаштування клієнта тестування перед кожним тестом."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_all_products_page(self):
        """Тест маршруту /products/all (список усіх товарів)."""
        response = self.client.get("/products/all")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)
        self.assertIn(b"Phone", response.data)
        self.assertIn(b"PC", response.data)

    def test_detail_product_page(self):
        """Тест маршруту /products/all/<id> (детальна сторінка товару)."""
        response = self.client.get("/products/all/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)
        self.assertIn(b"1200", response.data)

    def test_product_not_found(self):
        """Тест маршруту /products/all/<id> для неіснуючого товару (404)."""
        response = self.client.get("/products/all/999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
