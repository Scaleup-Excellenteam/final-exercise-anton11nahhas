from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, UUID
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship, DeclarativeBase
from typing import List, Optional


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30))
    uploads: Mapped[List["Upload"]] = relationship(back_populates="user")


class Upload(Base):
    __tablename__ = "uploads_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[UUID] = mapped_column(UUID)
    file_name: Mapped[str] = mapped_column(String(10))
    upload_time: Mapped[str] = mapped_column(String)
    finish_time: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped["User"] = relationship(back_populates="uploads")

