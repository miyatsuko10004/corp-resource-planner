from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class SkillBase(BaseModel):
    name: str

class Skill(SkillBase):
    id: int
    class Config:
        orm_mode = True

class UnitCostBase(BaseModel):
    amount: int
    start_date: date
    end_date: Optional[date] = None

class EmployeeCreate(BaseModel):
    name: str
    email: str
    role: str
    skills: List[str] = []
    unit_cost: int

class Employee(BaseModel):
    id: int
    name: str
    email: str
    role: str
    skills: List[Skill] = []
    
    class Config:
        orm_mode = True
