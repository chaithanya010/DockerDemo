# app/models/employee.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column # Using newer 2.0 style annotations

from app.db.base import Base # Import the Base we defined

class Employee(Base):
    __tablename__ = "employees" # Table name in the database

    # Using Mapped and mapped_column (SQLAlchemy 2.0 style) is recommended
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    # Optional: Add a __repr__ for helpful debugging printouts
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}', email='{self.email}')>"