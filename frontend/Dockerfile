FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn jinja2 python-multipart httpx
COPY . /app
# Note: Adjust template directory path in main.py if needed, or rely on relative path from working dir
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
