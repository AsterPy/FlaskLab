import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
DEBUG = True
WTF_CSRF_ENABLED = True

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_DB_PATH = os.path.join(DATA_DIR, "products.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "products", "static", "uploads")
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

