from flask import request, redirect, url_for, render_template, flash, session, make_response
from . import users_bp

VALID_USERS = {
    "admin": "12345",
    "user": "password"
}


@users_bp.route("/hi/<string:name>")  
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)

    return render_template(
        "hi.html",
        title="Greetings",
        name=name,
        age=age
    )


@users_bp.route("/admin")
def admin():
    to_url = url_for("users.greetings", name="administrator", age=45, _external=True)
    print(to_url)
    return redirect(to_url)


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username in VALID_USERS and VALID_USERS[username] == password:
            session["username"] = username
            flash("Ви успішно увійшли в систему!", "success")
            return redirect(url_for("users.profile"))
        else:
            flash("Невірне ім'я користувача або пароль!", "danger")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login")


@users_bp.route("/profile", methods=["GET", "POST"])
def profile():
    username = session.get("username")
    if not username:
        flash("Будь ласка, увійдіть у систему для перегляду профілю.", "danger")
        return redirect(url_for("users.login"))

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
def set_theme(theme):
    if theme not in ("light", "dark"):
        theme = "light"
    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie("theme", theme, max_age=60 * 60 * 24 * 30)
    flash(f"Кольорову схему змінено на: {theme}", "info")
    return response


@users_bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("username", None)
    flash("Ви вийшли з системи.", "info")
    return redirect(url_for("users.login"))


