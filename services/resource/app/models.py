from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from .database import Base
from datetime import date

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String)

    skills = relationship("Skill", secondary="employee_skills", back_populates="employees")
    unit_costs = relationship("UnitCost", back_populates="employee")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    employees = relationship("Employee", secondary="employee_skills", back_populates="skills")

class EmployeeSkill(Base):
    __tablename__ = "employee_skills"
    employee_id = Column(Integer, ForeignKey("employees.id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)

class UnitCost(Base):
    __tablename__ = "unit_costs"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    amount = Column(Integer)
    start_date = Column(Date, default=date.today)
    end_date = Column(Date, nullable=True) # None means 'Current'

    employee = relationship("Employee", back_populates="unit_costs")
