from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Enum as SqEnum
from sqlalchemy.orm import relationship
from .database import Base
import enum

class ProjectStatus(str, enum.Enum):
    LEAD = "Lead"
    PROPOSAL = "Proposal"
    CONTRACTED = "Contracted"
    COMPLETED = "Completed"
    LOST = "Lost"

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String) # Consultant, Manager, Partner, etc.
    unit_cost = Column(Integer, default=800000) # Monthly standard cost
    skills = Column(String, default="") # Comma-separated (e.g., "Python,AWS")
    industries = Column(String, default="") # Comma-separated (e.g., "Finance,Retail")
    
    assignments = relationship("ProjectAssignment", back_populates="employee")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    industry = Column(String)

    projects = relationship("Project", back_populates="customer")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String, default=ProjectStatus.LEAD)
    contract_amount = Column(Integer) # Total amount
    start_date = Column(Date)
    end_date = Column(Date)
    payment_terms = Column(String) # e.g., "End of next month"

    customer = relationship("Customer", back_populates="projects")
    assignments = relationship("ProjectAssignment", back_populates="project")
    billings = relationship("Billing", back_populates="project")

class ProjectAssignment(Base):
    __tablename__ = "project_assignments"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    effort_percent = Column(Integer) # 0-100%

    project = relationship("Project", back_populates="assignments")
    employee = relationship("Employee", back_populates="assignments")

class Billing(Base):
    __tablename__ = "billings"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    billing_date = Column(Date) # Represents the billing month
    amount = Column(Integer)
    status = Column(String) # Sent, Paid, etc.

    project = relationship("Project", back_populates="billings")
