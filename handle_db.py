from datetime import datetime
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, UUID, create_engine, DateTime
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship, DeclarativeBase
from typing import List, Optional


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    This class inherits from the Base class, the class represents a user table in the database, it first declares
    its name, then declares the column names and their datatypes, and finally a relationship with the uploads table,
    a one-to-many relationship, meaning a single user could have multiple uploads, with the help of back_populates
    parameter it helps to establish a bidirectional relationship.
    the attributes the table holds:
    -id: the id of a user, which is set to primary key.
    -email: the user's email.
    """
    __tablename__ = "users_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30))
    uploads: Mapped[List["Upload"]] = relationship(back_populates="user")


class Upload(Base):
    """
    This class also inherits from the Base class and also represents another table in the database, this table holds
    7 attributes, and established another bidirectional relationship with the user table, Multiple upload could belong
    to a single user. The attribute that this table holds:
    -id: generated id of the upload, which is set to a primary key.
    -uid: generated universal unique ID of the upload.
    -file_name: the name of the file uploaded.
    -upload_time: the time the file was uploaded.
    -finish_time: the time the file finished uploading.
    -status: the current status the file is holding.
    -user_id: the id of the user, which is set as a foreign key.
    """
    __tablename__ = "uploads_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[UUID] = mapped_column(UUID)
    file_name: Mapped[str] = mapped_column(String(10))
    upload_time: Mapped[datetime] = mapped_column(String)
    finish_time: Mapped[datetime] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped["User"] = relationship(back_populates="uploads")


def main():
    engine = create_engine("sqlite://", echo=True)

    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
