from flask import Blueprint
from .db import close_db

products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/product",
    template_folder="templates/products",
    static_folder="static"
)

products_bp.teardown_app_request(close_db)

from . import views
