import os
from datetime import datetime
from tinydb import TinyDB, Query
from flask import g, current_app, has_app_context


def get_db():
    if has_app_context():
        if "tinydb" not in g:
            db_path = current_app.config.get("PRODUCTS_DB_PATH")
            if not db_path:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                db_path = os.path.join(base_dir, "data", "products.json")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            g.tinydb = TinyDB(db_path)
        return g.tinydb

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    db_path = os.path.join(base_dir, "data", "products.json")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return TinyDB(db_path)


def close_db(e=None):
    db = g.pop("tinydb", None)
    if db is not None:
        db.close()


def get_products_table():
    db = get_db()
    table = db.table("products")
    if len(table) == 0:
        initial_products = [
            {
                "id": 1,
                "name": "Laptop",
                "price": 1200.00,
                "category": "electronics",
                "quantity": 10,
                "image": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": "Потужний ноутбук з процесором Intel Core i7, 16 ГБ оперативної пам’яті та SSD на 512 ГБ."
            },
            {
                "id": 2,
                "name": "Phone",
                "price": 800.00,
                "category": "electronics",
                "quantity": 15,
                "image": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": "Смартфон із 6.5-дюймовим OLED-дисплеєм, подвійною камерою та акумулятором на 5000мА·год."
            },
            {
                "id": 3,
                "name": "PC",
                "price": 1800.00,
                "category": "electronics",
                "quantity": 5,
                "image": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": "Настільний комп’ютер для ігор або роботи з графікою: RTX 4070, 32 ГБ RAM, 1 ТБ SSD."
            }
        ]
        table.insert_multiple(initial_products)
    return table
