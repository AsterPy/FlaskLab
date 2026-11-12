import os
import logging
from flask import request, redirect, url_for, render_template, abort, flash
from .forms import ContactForm

contact_logger = logging.getLogger("contact_logger")
contact_logger.setLevel(logging.INFO)


def init_logger(app):
    if not contact_logger.handlers:
        data_dir = app.config.get("DATA_DIR", os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "data"))
        os.makedirs(data_dir, exist_ok=True)
        log_file_path = os.path.join(data_dir, "contact.log")
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        contact_logger.addHandler(file_handler)


def resume():
    return render_template(
        "resume.html",
        title="Resume"
    )


def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact_logger.info(
            f"Contact form submitted: name='{form.name.data}', email='{form.email.data}', "
            f"phone='{form.phone.data}', subject='{form.subject.data}', message='{form.message.data}'"
        )
        flash("Ваше повідомлення успішно надіслано!", "success")
        return redirect(url_for("contact"))
    elif request.method == "POST":
        contact_logger.warning(f"Contact form validation failed: {form.errors}")
        flash("Помилка валідації форми. Перевірте введені дані.", "danger")

    return render_template(
        "contacts.html",
        title="Contacts",
        form=form
    )


def home():
    agent = request.user_agent
    return render_template("homepage.html", title="Homepage", agent=agent)


def products_redirect():
    return redirect(url_for("products.all_products"))


def register_routes(app):
    init_logger(app)
    app.add_url_rule("/resume", "resume", resume)
    app.add_url_rule("/contact", "contact", contact, methods=["GET", "POST"])
    app.add_url_rule("/contacts", "contacts", contact, methods=["GET", "POST"])
    app.add_url_rule("/", "home", home)
    app.add_url_rule("/homepage", "home", home)
    app.add_url_rule("/products", "products_redirect", products_redirect)
    app.add_url_rule("/products/all", "products_redirect", products_redirect)
