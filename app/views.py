import os
import logging
from flask import request, redirect, url_for, render_template, abort, flash
from . import app
from .forms import ContactForm

contact_logger = logging.getLogger("contact_logger")
contact_logger.setLevel(logging.INFO)
if not contact_logger.handlers:
    data_dir = app.config.get("DATA_DIR", os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    log_file_path = os.path.join(data_dir, "contact.log")
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    contact_logger.addHandler(file_handler)


@app.route("/resume")
def resume():
    return render_template(
        "resume.html",
        title="Resume"
    )


@app.route("/contact", methods=["GET", "POST"], endpoint="contact")
@app.route("/contacts", methods=["GET", "POST"], endpoint="contacts")
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


@app.route("/")
@app.route("/homepage")
def home():
    agent = request.user_agent
    return render_template("homepage.html", title="Homepage", agent=agent)


@app.route("/products")
@app.route("/products/all")
def products_redirect():
    return redirect(url_for("products.all_products"))
