from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db

if TYPE_CHECKING:
    from app.users.models import User


# Асоціативна таблиця для зв'язку "багато до багатьох"
post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True)
)


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
    category: Mapped[str] = mapped_column(
        Enum("news", "publication", "tech", "other", name="post_categories"),
        default="other",
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="posts")

    # Зв'язок "багато до багатьох" з тегами
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tags, back_populates="posts")

    @property
    def author(self) -> str:
        if self.user:
            return self.user.username
        if hasattr(self, "_author_name") and self._author_name:
            return self._author_name
        return "Anonymous"

    @author.setter
    def author(self, value: str) -> None:
        self._author_name = value

    def __repr__(self) -> str:
        return f"<Post(title={self.title})>"


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Зв'язок "багато до багатьох" з постами
    posts: Mapped[list["Post"]] = relationship(secondary=post_tags, back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag(name='{self.name}')>"
