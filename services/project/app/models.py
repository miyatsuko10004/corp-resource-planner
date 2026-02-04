from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    customer_id = Column(Integer) # Mock foreign key (Customer is in another service or shared lib)
    contract_amount = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default="Lead")

    assignments = relationship("Assignment", back_populates="project")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    employee_id = Column(Integer) # ID from Resource Service
    start_date = Column(Date)
    end_date = Column(Date)

    project = relationship("Project", back_populates="assignments")
    allocations = relationship("Allocation", back_populates="assignment")

class Allocation(Base):
    __tablename__ = "allocations"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    month = Column(String) # YYYY-MM
    effort_percent = Column(Integer)

    assignment = relationship("Assignment", back_populates="allocations")
