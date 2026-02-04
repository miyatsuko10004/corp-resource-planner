from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/employees/", response_model=schemas.Employee, status_code=201)
def create_employee(emp: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Check email
    db_emp = db.query(models.Employee).filter(models.Employee.email == emp.email).first()
    if db_emp:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create Employee
    new_emp = models.Employee(name=emp.name, email=emp.email, role=emp.role)
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    
    # Handle Skills (Normalize)
    for skill_name in emp.skills:
        skill = db.query(models.Skill).filter(models.Skill.name == skill_name).first()
        if not skill:
            skill = models.Skill(name=skill_name)
            db.add(skill)
            db.commit()
            db.refresh(skill)
        new_emp.skills.append(skill)
    
    # Handle Unit Cost (Initial History)
    initial_cost = models.UnitCost(employee_id=new_emp.id, amount=emp.unit_cost)
    db.add(initial_cost)
    
    db.commit()
    db.refresh(new_emp)
    return new_emp

@app.get("/employees/{employee_id}", response_model=schemas.Employee)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if db_emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_emp

@app.get("/employees/", response_model=List[schemas.Employee])
def list_employees(skill: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Employee)
    if skill:
        query = query.join(models.Employee.skills).filter(models.Skill.name == skill)
    return query.all()
