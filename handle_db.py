import uuid
from datetime import datetime
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, UUID, create_engine, DateTime, \
    CheckConstraint
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

    id = mapped_column(Integer, primary_key=True, unique=True)
    email = mapped_column(String(30), unique=True, nullable=False)
    uploads = relationship('Upload', back_populates="user", cascade="all, delete-orphan")


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

    id = mapped_column(Integer, primary_key=True, unique=True)
    uid = mapped_column(UUID, nullable=False, unique=True)
    file_name = mapped_column(String, default="Default_file")
    upload_time = mapped_column(DateTime, nullable=False)
    finish_time = mapped_column(DateTime)
    status = mapped_column(String, nullable=False)
    user_id = mapped_column(Integer, ForeignKey("user_table.id"), default="N/A", nullable=False)
    user = relationship('User', back_populates="uploads", cascade="all")

    __table_args__ = (
        CheckConstraint(finish_time >= upload_time, name='check_finish_time_after_upload_time')
    )

    def __init__(self, filename: str, status: str, uid: uuid, user_id: int = None):
        self.file_name = filename
        self.status = status
        self.uid = uuid.uuid4()
        self.upload_time = datetime.now()
        self.uid = uid
        self.user_id = user_id

    def upload_path(self) -> str:
        return f"/uploads/{self.uid}/{self.file_name}"



def main():
    engine = create_engine("sqlite://", echo=True)

    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
