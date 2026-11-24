from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    DateTimeLocalField
)
from wtforms.validators import DataRequired, Length, Optional
from sqlalchemy import select
from app import db
from app.users.models import User
from app.posts.models import Tag


class PostForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Title is required"),
            Length(max=150, message="Title must not exceed 150 characters")
        ]
    )
    content = TextAreaField(
        "Content",
        validators=[
            DataRequired(message="Content is required")
        ]
    )
    category = SelectField(
        "Category",
        choices=[
            ("news", "News"),
            ("publication", "Publication"),
            ("tech", "Tech"),
            ("other", "Other")
        ],
        default="other",
        validators=[
            DataRequired(message="Category is required")
        ]
    )
    publish_date = DateTimeLocalField(
        "Publish Date",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()]
    )
    author_id = SelectField(
        "Author",
        coerce=int,
        validators=[Optional()]
    )
    tags = SelectMultipleField(
        "Tags",
        coerce=int,
        validators=[Optional()]
    )
    enabled = BooleanField(
        "Is this post active?",
        default=True
    )
    submit = SubmitField("Add Post")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            authors = db.session.scalars(select(User).order_by(User.id)).all()
            self.author_id.choices = [(a.id, a.username) for a in authors]

            tags = db.session.scalars(select(Tag).order_by(Tag.id)).all()
            self.tags.choices = [(t.id, t.name) for t in tags]
        except Exception:
            self.author_id.choices = []
            self.tags.choices = []
