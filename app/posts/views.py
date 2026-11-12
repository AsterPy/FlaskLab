from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request, session
from app import db
from . import post_bp
from .models import Post
from .forms import PostForm


@post_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            is_active=form.enabled.data,
            author=session.get("username") or "Anonymous",
            posted=form.publish_date.data if form.publish_date.data else datetime.now(timezone.utc).replace(tzinfo=None)
        )
        db.session.add(post)
        db.session.commit()
        flash("Post added successfully", "success")
        return redirect(url_for("posts.all_posts"))

    return render_template("add_post.html", form=form, title="Create Post", is_edit=False)


@post_bp.route("", methods=["GET"])
@post_bp.route("/", methods=["GET"])
def all_posts():
    stmt = db.select(Post).where(Post.is_active.is_(True)).order_by(Post.posted.desc())
    post_list = db.session.scalars(stmt).all()
    return render_template("posts.html", posts=post_list, title="All Posts")


posts = all_posts


@post_bp.route("/<int:id>", methods=["GET"])
def detail_post(id):
    post = db.get_or_404(Post, id)
    return render_template("detail_post.html", post=post, title=post.title)


post_detail = detail_post


@post_bp.route("/<int:id>/update", methods=["GET", "POST"])
@post_bp.route("/update/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    post = db.get_or_404(Post, id)
    form = PostForm(obj=post)

    if request.method == "GET":
        form.publish_date.data = post.posted
        form.enabled.data = post.is_active

    if form.validate_on_submit():
        form.populate_obj(post)
        post.is_active = form.enabled.data
        if form.publish_date.data:
            post.posted = form.publish_date.data
        db.session.commit()
        flash("Post updated successfully", "success")
        return redirect(url_for("posts.all_posts"))

    return render_template("add_post.html", form=form, post=post, title="Edit Post", is_edit=True)


update_post = edit_post


@post_bp.route("/<int:id>/delete", methods=["GET", "POST"])
@post_bp.route("/delete/<int:id>", methods=["GET", "POST"])
def delete_post(id):
    post = db.get_or_404(Post, id)
    if request.method == "POST":
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted successfully", "success")
        return redirect(url_for("posts.all_posts"))

    return render_template("delete_confirm.html", post=post, title="Delete Post")
