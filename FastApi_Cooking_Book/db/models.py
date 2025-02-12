from os import getenv
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

engine = create_engine(getenv('DATABASE_URL'))


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Recipe(Base):
    __tablename__ = 'recipe'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete")
    steps = relationship("Step", back_populates="recipe", cascade="all, delete")


class Ingredient(Base):
    __tablename__ = 'ingredient'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    quantity = Column(String, default='По вкусу')
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    recipe = relationship("Recipe", back_populates="ingredients")


class Step(Base):
    __tablename__ = 'step'
    id = Column(Integer, primary_key=True, autoincrement=True)
    step_description = Column(String)
    step_time = Column(Integer)
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    recipe = relationship('Recipe', back_populates='steps')


class UniqueIngredient(Base):
    __tablename__ = 'unique_ingredient'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


Base.metadata.create_all(engine)
