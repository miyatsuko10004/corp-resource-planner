from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

RESOURCE_SERVICE_URL = "http://resource-service:8000"
PROJECT_SERVICE_URL = "http://project-service:8000"

@app.get("/employees", response_class=HTMLResponse)
async def employee_list(request: Request, q: str = None):
    async with httpx.AsyncClient() as client:
        # Call Resource Service
        params = {"skill": q} if q else {}
        # Resource Service's list API currently filters by exact skill match via query param
        # We might need to enhance Resource Service for full text search later, 
        # but for now let's use the endpoint we made.
        # Note: Previous TDD implemented /employees/?skill=...
        # We should map 'q' to 'skill' for compatibility or update Resource Service.
        
        # Let's assume we fetch all and filter in BFF for now if the API doesn't support rich search yet,
        # OR just pass the skill param if provided.
        resp = await client.get(f"{RESOURCE_SERVICE_URL}/employees/", params=params)
        employees = resp.json() if resp.status_code == 200 else []
        
        # We need heatmap data too. In a real microservices world, we'd fetch assignments from Project Service
        # and merge. For this simplified step, we'll just display the employee list from Resource Service.
        
    return templates.TemplateResponse("employees.html", {
        "request": request, 
        "employees": employees,
        "month_headers": [] # Heatmap temporarily disabled until Project Service integration is full
    })
