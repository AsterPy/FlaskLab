import os
import uuid
from datetime import datetime
from flask import request, redirect, url_for, render_template, abort, flash, current_app
from tinydb import Query
from . import products_bp
from .db import get_products_table
from ..forms import ProductForm


def save_image(image_file):
    """Зберігає завантажене зображення з безпечним іменем UUID та повертає відносний шлях."""
    if not image_file or not getattr(image_file, "filename", None):
        return None
    ext = os.path.splitext(image_file.filename)[1].lower()
    if not ext:
        ext = ".jpg"
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    upload_folder = current_app.config.get("UPLOAD_FOLDER")
    if not upload_folder:
        upload_folder = os.path.join(current_app.root_path, "products", "static", "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_filename)
    image_file.save(file_path)
    return f"uploads/{unique_filename}"


@products_bp.route("", methods=["GET"], endpoint="all_products")
@products_bp.route("/", methods=["GET"])
@products_bp.route("/all", methods=["GET"])
def all_products():
    table = get_products_table()
    products = table.all()
    return render_template("products.html", products=products)


@products_bp.route("/add", methods=["GET", "POST"], endpoint="add_product")
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        image_path = save_image(form.image.data)
        table = get_products_table()
        all_items = table.all()
        new_id = max([item.get("id", 0) for item in all_items], default=0) + 1
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_product = {
            "id": new_id,
            "name": form.name.data,
            "content": form.content.data,
            "price": round(float(form.price.data), 2),
            "category": form.category.data,
            "quantity": int(form.quantity.data),
            "image": image_path,
            "created_at": created_at
        }
        table.insert(new_product)
        flash(f"Товар «{form.name.data}» успішно додано!", "success")
        return redirect(url_for("products.all_products"))
    elif request.method == "POST":
        flash("Помилка валідації форми. Перевірте введені дані.", "danger")

    return render_template("add_product.html", form=form)


@products_bp.route("/<int:id>", methods=["GET"], endpoint="get_product")
@products_bp.route("/all/<int:id>", methods=["GET"])
def get_product(id):
    table = get_products_table()
    product_query = Query()
    results = table.search(product_query.id == id)
    if not results:
        abort(404)
    product = results[0]
    return render_template("detail_product.html", product=product)


@products_bp.route("/<int:id>/edit", methods=["GET", "POST"], endpoint="edit_product")
def edit_product(id):
    table = get_products_table()
    product_query = Query()
    results = table.search(product_query.id == id)
    if not results:
        abort(404)
    product = results[0]

    form = ProductForm()

    if request.method == "GET":
        form.name.data = product.get("name")
        form.content.data = product.get("content")
        form.price.data = product.get("price")
        form.category.data = product.get("category")
        form.quantity.data = product.get("quantity")

    if form.validate_on_submit():
        new_image_path = save_image(form.image.data)
        image_path = new_image_path if new_image_path else product.get("image")

        updated_data = {
            "id": product["id"],
            "name": form.name.data,
            "content": form.content.data,
            "price": round(float(form.price.data), 2),
            "category": form.category.data,
            "quantity": int(form.quantity.data),
            "image": image_path,
            "created_at": product["created_at"]
        }
        table.update(updated_data, product_query.id == id)
        flash(f"Товар «{form.name.data}» успішно оновлено!", "success")
        return redirect(url_for("products.get_product", id=id))
    elif request.method == "POST":
        flash("Помилка валідації форми. Перевірте введені дані.", "danger")

    return render_template("edit_product.html", form=form, product=product)


@products_bp.route("/<int:id>/delete", methods=["POST"], endpoint="delete_product")
def delete_product(id):
    table = get_products_table()
    product_query = Query()
    results = table.search(product_query.id == id)
    if not results:
        abort(404)
    product = results[0]

    table.remove(product_query.id == id)
    flash(f"Товар «{product.get('name')}» успішно видалено!", "success")
    return redirect(url_for("products.all_products"))
