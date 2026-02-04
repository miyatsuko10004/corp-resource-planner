from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db, engine, Base
from app.models import Project, Employee, Customer, ProjectStatus, ProjectAssignment

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Dashboard / Project List
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "projects": projects})

# Create Project Form
@app.get("/projects/new", response_class=HTMLResponse)
def new_project_form(request: Request, db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return templates.TemplateResponse("project_form.html", {"request": request, "customers": customers, "statuses": list(ProjectStatus)})

@app.post("/projects", response_class=HTMLResponse)
def create_project(
    request: Request,
    name: str = Form(...),
    customer_id: int = Form(...),
    status: str = Form(...),
    contract_amount: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    db: Session = Depends(get_db)
):
    new_proj = Project(
        name=name,
        customer_id=customer_id,
        status=status,
        contract_amount=contract_amount,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        payment_terms="月末締め翌月末払い"
    )
    db.add(new_proj)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(request: Request, project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return RedirectResponse(url="/")
        
    # Calculate Costs
    total_cost = 0
    breakdown = []
    
    for assign in project.assignments:
        # Approximate duration in months
        days = (assign.end_date - assign.start_date).days
        months = days / 30.0
        
        # Cost = Monthly Unit Cost * Months * Effort%
        cost = int(assign.employee.unit_cost * months * (assign.effort_percent / 100.0))
        total_cost += cost
        
        breakdown.append({
            "name": assign.employee.name,
            "role": assign.employee.role,
            "effort": assign.effort_percent,
            "cost": cost
        })
        
    profit = project.contract_amount - total_cost
    margin_percent = (profit / project.contract_amount * 100) if project.contract_amount > 0 else 0
    
    summary = {
        "revenue": project.contract_amount,
        "cost": total_cost,
        "profit": profit,
        "margin_percent": margin_percent,
        "breakdown": breakdown
    }

    return templates.TemplateResponse("project_detail.html", {
        "request": request, 
        "project": project, 
        "summary": summary
    })

from datetime import date, timedelta
from calendar import monthrange

# ... (imports)

def get_monthly_utilization(employee, start_date, months=6):
    utilization = []
    current_year = start_date.year
    current_month = start_date.month

    for _ in range(months):
        month_start = date(current_year, current_month, 1)
        _, last_day = monthrange(current_year, current_month)
        month_end = date(current_year, current_month, last_day)
        
        total_effort = 0
        for assign in employee.assignments:
            # Check overlap
            if assign.start_date <= month_end and assign.end_date >= month_start:
                total_effort += assign.effort_percent
        
        utilization.append({
            "year": current_year,
            "month": current_month,
            "label": f"{current_year}/{current_month:02d}",
            "percent": total_effort
        })

        # Next month
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1
            
    return utilization

from sqlalchemy import or_

# ...

# Employee List (Resource Management)
@app.get("/employees", response_class=HTMLResponse)
def employee_list(request: Request, q: str = None, db: Session = Depends(get_db)):
    query = db.query(Employee)
    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                Employee.name.like(search),
                Employee.skills.like(search),
                Employee.industries.like(search),
                Employee.role.like(search)
            )
        )
    employees = query.all()
    today = date.today()
    
    # Attach utilization data to each employee object (runtime only)
    for emp in employees:
        emp.heatmap = get_monthly_utilization(emp, today)
        
    # Get month headers from the first employee (or calculate fresh if list empty)
    month_headers = []
    if employees:
        month_headers = [m["label"] for m in employees[0].heatmap]
    
    return templates.TemplateResponse("employees.html", {
        "request": request, 
        "employees": employees,
        "month_headers": month_headers
    })
