from flask import request, redirect, url_for, render_template, abort
from . import app

@app.route("/resume")
def resume():
    return render_template(
        "resume.html",
        title="Resume"
    )


@app.route("/contacts")
def contacts():
    return render_template(
        "contacts.html",
        title="Contacts"
    )

@app.route("/")
@app.route("/homepage")
def home():
    agent = request.user_agent
    return render_template("homepage.html", title="Homepage", agent=agent)
