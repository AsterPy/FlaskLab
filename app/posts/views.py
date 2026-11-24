from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request, session
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from app import db
from app.users.models import User
from . import post_bp
from .models import Post, Tag
from .forms import PostForm


@post_bp.route("/create", methods=["GET", "POST"])
@post_bp.route("/add_post", methods=["GET", "POST"])
def create_post():
    form = PostForm()

    authors = db.session.scalars(select(User).order_by(User.id)).all()
    form.author_id.choices = [(author.id, author.username) for author in authors]

    all_tags = db.session.scalars(select(Tag).order_by(Tag.id)).all()
    form.tags.choices = [(tag.id, tag.name) for tag in all_tags]

    if form.validate_on_submit():
        user_id = form.author_id.data if form.author_id.data else None
        if not user_id and session.get("username"):
            session_user = db.session.scalar(select(User).where(User.username == session.get("username")))
            if not session_user:
                session_user = User(
                    username=session.get("username"),
                    email=f"{session.get('username')}@example.com",
                    password="password"
                )
                db.session.add(session_user)
                db.session.flush()
            user_id = session_user.id

        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            is_active=form.enabled.data,
            user_id=user_id,
            posted=form.publish_date.data if form.publish_date.data else datetime.now(timezone.utc).replace(tzinfo=None)
        )
        if session.get("username"):
            post.author = session.get("username")

        if form.tags.data:
            selected_tags = db.session.scalars(select(Tag).where(Tag.id.in_(form.tags.data))).all()
            post.tags = list(selected_tags)

        db.session.add(post)
        db.session.commit()
        flash("Post added successfully", "success")
        return redirect(url_for("posts.all_posts"))

    return render_template("add_post.html", form=form, title="Create Post", is_edit=False)


@post_bp.route("", methods=["GET"])
@post_bp.route("/", methods=["GET"])
def all_posts():
    stmt = (
        select(Post)
        .options(
            joinedload(Post.user),
            selectinload(Post.tags),
        )
        .where(Post.is_active.is_(True))
        .order_by(Post.posted.desc())
    )
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

    authors = db.session.scalars(select(User).order_by(User.id)).all()
    form.author_id.choices = [(author.id, author.username) for author in authors]

    all_tags = db.session.scalars(select(Tag).order_by(Tag.id)).all()
    form.tags.choices = [(tag.id, tag.name) for tag in all_tags]

    if request.method == "GET":
        form.publish_date.data = post.posted
        form.enabled.data = post.is_active
        form.author_id.data = post.user_id
        form.tags.data = [t.id for t in post.tags]

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        post.is_active = form.enabled.data
        if form.publish_date.data:
            post.posted = form.publish_date.data
        post.user_id = form.author_id.data if form.author_id.data else None

        if form.tags.data:
            selected_tags = db.session.scalars(select(Tag).where(Tag.id.in_(form.tags.data))).all()
            post.tags = list(selected_tags)
        else:
            post.tags = []

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
