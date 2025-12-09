from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    pets = relationship("Pet", back_populates="user", cascade="all, delete-orphan")


class Pet(Base):
    __tablename__ = "pets"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uix_user_petname"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    breed = Column(String, nullable=False)
    name = Column(String, nullable=False)
    age = Column(String, nullable=False)
    extra_info = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="pets")
    notes = relationship("Note", back_populates="pet", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    period = Column(String, nullable=False)  # one of expected values
    extra_info = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    pet = relationship("Pet", back_populates="notes")
