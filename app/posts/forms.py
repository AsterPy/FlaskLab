from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, Optional


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
    enabled = BooleanField(
        "Enabled",
        default=True
    )
    submit = SubmitField("Save Post")
