import random
from datetime import date, timedelta
from faker import Faker
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models import Employee, Customer, Project, ProjectAssignment, Billing, ProjectStatus

fake = Faker('ja_JP')

def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data
    db.query(Billing).delete()
    db.query(ProjectAssignment).delete()
    db.query(Project).delete()
    db.query(Customer).delete()
    db.query(Employee).delete()
    db.commit()

    print("Seeding Employees...")
    roles = {
        "Partner": 2000000,
        "Senior Manager": 1600000,
        "Manager": 1300000,
        "Senior Consultant": 1000000,
        "Consultant": 800000,
        "Analyst": 600000
    }
    skill_set = ["Python", "Java", "AWS", "Azure", "SAP", "Salesforce", "React", "PMO", "Data Analysis"]
    industry_set = ["Finance", "Manufacturing", "Retail", "Healthcare", "Public", "Telco"]

    employees = []
    for _ in range(50):
        role_name = random.choice(list(roles.keys()))
        emp = Employee(
            name=fake.name(),
            email=fake.email(),
            role=role_name,
            unit_cost=roles[role_name],
            skills=",".join(random.sample(skill_set, k=random.randint(1, 3))),
            industries=",".join(random.sample(industry_set, k=random.randint(1, 2)))
        )
        db.add(emp)
        employees.append(emp)
    db.commit()

    print("Seeding Customers...")
    customers = []
    industries = ["Finance", "Manufacturing", "Retail", "Healthcare", "Technology"]
    for _ in range(10):
        cust = Customer(
            name=fake.company(),
            industry=random.choice(industries)
        )
        db.add(cust)
        customers.append(cust)
    db.commit()

    print("Seeding Projects & Assignments...")
    for _ in range(30):
        start_dt = fake.date_between(start_date='-1y', end_date='+1y')
        duration = random.randint(3, 12) * 30
        end_dt = start_dt + timedelta(days=duration)
        
        status_val = random.choice(list(ProjectStatus))
        
        proj = Project(
            name=f"基幹システム構築: {fake.bs()}",
            customer_id=random.choice(customers).id,
            status=status_val,
            contract_amount=random.randint(10, 100) * 1000000,
            start_date=start_dt,
            end_date=end_dt,
            payment_terms="月末締め翌月末払い"
        )
        db.add(proj)
        db.commit()

        # Assignments (Assign 2-5 people per project)
        team_size = random.randint(2, 5)
        assigned_members = random.sample(employees, team_size)
        
        for member in assigned_members:
            assign = ProjectAssignment(
                project_id=proj.id,
                employee_id=member.id,
                start_date=start_dt,
                end_date=end_dt,
                effort_percent=random.choice([20, 50, 80, 100])
            )
            db.add(assign)
        
        # Billings (Monthly)
        curr = start_dt
        while curr < end_dt:
            # Billing date is roughly end of month
            bill_date = curr.replace(day=28) 
            billing = Billing(
                project_id=proj.id,
                billing_date=bill_date,
                amount=proj.contract_amount // (duration // 30 + 1),
                status=random.choice(["Pending", "Sent", "Paid"])
            )
            db.add(billing)
            curr += timedelta(days=30)
            
    db.commit()
    print("Seeding Complete!")
    db.close()

if __name__ == "__main__":
    seed_data()
