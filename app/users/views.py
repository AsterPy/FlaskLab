from flask import request, redirect, url_for, render_template, flash, make_response
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import select
from app import db
from . import users_bp
from .models import User
from .forms import RegistrationForm, LoginForm


@users_bp.route("/hi/<string:name>")
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)

    return render_template(
        "hi.html",
        title="Greetings",
        name=name,
        age=age,
    )


@users_bp.route("/admin")
def admin():
    to_url = url_for("users.greetings", name="administrator", age=45, _external=True)
    print(to_url)
    return redirect(to_url)


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        user.hash_password()
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("users.login"))

    return render_template("register.html", form=form, title="Register")


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(select(User).where(User.email == form.email.data))
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("You have been logged in!", "success")
            return redirect(url_for("users.account"))
        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form, title="Login")


@users_bp.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account", user=current_user)


@users_bp.route("/")
@login_required
def all_users():
    users = db.session.scalars(select(User).order_by(User.id)).all()
    return render_template("users.html", title="Users List", users=users)


@users_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    username = current_user.username

    if request.method == "POST":
        action = request.form.get("action")
        response = make_response(redirect(url_for("users.profile")))

        if action == "add":
            key = request.form.get("key", "").strip()
            value = request.form.get("value", "").strip()
            max_age_raw = request.form.get("max_age", "").strip()

            if key and value:
                max_age = int(max_age_raw) if max_age_raw.isdigit() else None
                response.set_cookie(key, value, max_age=max_age)
                flash(f"Кукі '{key}' успішно додано!", "success")
                return response
            else:
                flash("Вкажіть ключ та значення для кукі.", "warning")
                return redirect(url_for("users.profile"))

        elif action == "delete":
            key = request.form.get("key", "").strip()
            if key and key in request.cookies:
                response.delete_cookie(key)
                flash(f"Кукі '{key}' успішно видалено!", "info")
                return response
            else:
                flash(f"Кукі з ключем '{key}' не знайдено.", "warning")
                return redirect(url_for("users.profile"))

        elif action == "delete_all":
            for cookie_key in request.cookies:
                if cookie_key != "session":
                    response.delete_cookie(cookie_key)
            flash("Усі кукі успішно видалено!", "info")
            return response

    cookies = request.cookies
    theme = request.cookies.get("theme", "light")
    return render_template("profile.html", title="Profile", username=username, cookies=cookies, theme=theme)


@users_bp.route("/set-theme/<string:theme>")
@login_required
def set_theme(theme):
    if theme not in ("light", "dark"):
        theme = "light"
    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie("theme", theme, max_age=60 * 60 * 24 * 30)
    flash(f"Кольорову схему змінено на: {theme}", "info")
    return response


@users_bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    flash("You have successfully logged out.", "info")
    return redirect(url_for("users.login"))
