from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/projects/", response_model=schemas.Project, status_code=201)
def create_project(proj: schemas.ProjectCreate, db: Session = Depends(get_db)):
    new_proj = models.Project(**proj.dict())
    db.add(new_proj)
    db.commit()
    db.refresh(new_proj)
    return new_proj

@app.post("/projects/{project_id}/assignments", response_model=schemas.Assignment, status_code=201)
def create_assignment(project_id: int, assign: schemas.AssignmentCreate, db: Session = Depends(get_db)):
    # Verify Project Exists
    proj = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create Assignment
    new_assign = models.Assignment(
        project_id=project_id,
        employee_id=assign.employee_id,
        start_date=assign.start_date,
        end_date=assign.end_date
    )
    db.add(new_assign)
    db.commit()
    db.refresh(new_assign)

    # Create Allocations
    for alloc in assign.allocations:
        new_alloc = models.Allocation(
            assignment_id=new_assign.id,
            month=alloc.month,
            effort_percent=alloc.effort_percent
        )
        db.add(new_alloc)
    
    db.commit()
    db.refresh(new_assign)
    return new_assign
