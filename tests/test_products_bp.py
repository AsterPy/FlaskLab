import io
import os
import shutil
import tempfile
import unittest
from app import app
from app.products.db import get_products_table, close_db


class ProductsBlueprintCRUDTestCase(unittest.TestCase):

    def setUp(self):
        """Налаштування тестового клієнта, ізольованої бази TinyDB та каталогу для завантажень."""
        temp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_db_path = temp_file.name
        temp_file.close()

        self.temp_upload_dir = tempfile.mkdtemp()

        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["PRODUCTS_DB_PATH"] = self.temp_db_path
        app.config["UPLOAD_FOLDER"] = self.temp_upload_dir
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()
        # Ініціалізація початкових даних
        get_products_table()

    def tearDown(self):
        """Прибирання тимчасової тестової бази та завантажених тестових файлів."""
        close_db()
        self.ctx.pop()
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except OSError:
                pass
        shutil.rmtree(self.temp_upload_dir, ignore_errors=True)

    # 1. READ (Перегляд)
    def test_product_list_page(self):
        """Тест маршруту GET /product (список товарів)."""
        response = self.client.get("/product")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Laptop".encode("utf-8"), response.data)
        self.assertIn("Phone".encode("utf-8"), response.data)
        self.assertIn("PC".encode("utf-8"), response.data)

    def test_product_detail_page(self):
        """Тест маршруту GET /product/<id> (детальна сторінка)."""
        response = self.client.get("/product/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Laptop".encode("utf-8"), response.data)
        self.assertIn("1200.00".encode("utf-8"), response.data)

    def test_product_not_found(self):
        """Тест повернення 404 для неіснуючого товару."""
        response = self.client.get("/product/999")
        self.assertEqual(response.status_code, 404)

    # 2. CREATE (Додавання)
    def test_add_product_get_form(self):
        """Тест відображення форми додавання товару GET /product/add."""
        response = self.client.get("/product/add")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Додати новий товар".encode("utf-8"), response.data)

    def test_add_product_post_valid(self):
        """Тест успішного додавання товару POST /product/add (PRG-патерн)."""
        product_data = {
            "name": "Tablet Pro",
            "content": "Потужний графічний планшет з чутливим стілусом",
            "price": "950.50",
            "category": "electronics",
            "quantity": "7"
        }
        response = self.client.post("/product/add", data=product_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Tablet Pro".encode("utf-8"), response.data)
        self.assertIn("успішно додано".encode("utf-8"), response.data)

    def test_add_product_with_image_upload(self):
        """Тест додавання товару з файлом зображення."""
        image_content = b"fake image content"
        product_data = {
            "name": "Headphones Wireless",
            "content": "Бездротові навушники з активним шумозаглушенням",
            "price": "299.99",
            "category": "electronics",
            "quantity": "25",
            "image": (io.BytesIO(image_content), "test_headphones.png")
        }
        response = self.client.post(
            "/product/add",
            data=product_data,
            content_type="multipart/form-data",
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Headphones Wireless".encode("utf-8"), response.data)

    def test_add_product_post_invalid(self):
        """Тест валідації форми: коротка назва або від'ємна ціна."""
        product_data = {
            "name": "No",  # менше 3 символів
            "content": "Опис",
            "price": "-50.00",  # від'ємна ціна
            "category": "electronics",
            "quantity": "5"
        }
        response = self.client.post("/product/add", data=product_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Помилка валідації форми".encode("utf-8"), response.data)

    # 3. UPDATE (Редагування)
    def test_edit_product_get_form(self):
        """Тест відображення форми редагування товару GET /product/<id>/edit."""
        response = self.client.get("/product/1/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Laptop".encode("utf-8"), response.data)

    def test_edit_product_post_valid(self):
        """Тест успішного оновлення товару POST /product/<id>/edit."""
        updated_data = {
            "name": "Laptop Ultra",
            "content": "Оновлений опис ноутбука з покращеною графікою",
            "price": "1450.00",
            "category": "electronics",
            "quantity": "8"
        }
        response = self.client.post("/product/1/edit", data=updated_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Laptop Ultra".encode("utf-8"), response.data)
        self.assertIn("успішно оновлено".encode("utf-8"), response.data)

    def test_edit_product_not_found(self):
        """Тест редагування неіснуючого товару (404)."""
        response = self.client.get("/product/999/edit")
        self.assertEqual(response.status_code, 404)

    # 4. DELETE (Видалення)
    def test_delete_product_post(self):
        """Тест видалення товару через POST-запит /product/<id>/delete."""
        response = self.client.post("/product/3/delete", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("успішно видалено".encode("utf-8"), response.data)
        # Перевірка що товару більше немає
        detail_response = self.client.get("/product/3")
        self.assertEqual(detail_response.status_code, 404)

    def test_delete_product_not_found(self):
        """Тест видалення неіснуючого товару (404)."""
        response = self.client.post("/product/999/delete")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
