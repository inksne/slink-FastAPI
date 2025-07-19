from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str]
    password: Mapped[str] = mapped_column(String(1024), nullable=False)

    links: Mapped[list["Link"]] = relationship("Link", back_populates="user", cascade="all, delete-orphan")


class Link(Base):
    __tablename__ = 'links'

    id: Mapped[int] = mapped_column(primary_key=True)
    long_link: Mapped[str] = mapped_column(nullable=False)
    short_link: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="links")