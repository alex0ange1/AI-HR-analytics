from datetime import date
from typing import Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, false
from project.infrastructure.postgres.database import Base
from sqlalchemy.dialects.postgresql import JSONB


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=false())


class Profession(Base):
    __tablename__ = "professions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    competencies: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str | None] = mapped_column(nullable=True)
    last_name: Mapped[str | None] = mapped_column(nullable=True)
    birth_date: Mapped[date | None] = mapped_column(nullable=True)
    city: Mapped[str | None] = mapped_column(nullable=True)

    phone: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str | None] = mapped_column(nullable=True)

    competencies: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
