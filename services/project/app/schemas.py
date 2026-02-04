from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class AllocationBase(BaseModel):
    month: str
    effort_percent: int

class Allocation(AllocationBase):
    id: int
    class Config:
        from_attributes = True

class AssignmentCreate(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    allocations: List[AllocationBase]

class Assignment(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    allocations: List[Allocation]
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    customer_id: int
    contract_amount: int
    start_date: date
    end_date: date

class Project(ProjectCreate):
    id: int
    status: str
    assignments: List[Assignment] = []
    class Config:
        from_attributes = True
