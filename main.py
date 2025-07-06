# Updated main.py with PostgreSQL integration
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, email: str = Form(...)):
    return templates.TemplateResponse("register.html", {"request": request, "email": email})

@app.post("/register", response_class=HTMLResponse)
def register(request: Request, name: str = Form(...), email: str = Form(...), event: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(models.EventRegistration).filter(models.EventRegistration.email == email).first()
    if existing:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Email already registered!"})

    new_entry = models.EventRegistration(name=name, email=email, event=event)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return templates.TemplateResponse("sucess.html", {"request": request, "name": name, "event": event, "email": email})

@app.post("/update-page", response_class=HTMLResponse)
def show_update_page(request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.EventRegistration).filter(models.EventRegistration.email == email).first()
    if user:
        return templates.TemplateResponse("update.html", {
            "request": request,
            "name": user.name,
            "email": user.email,
            "event": user.event
        })
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/update", response_class=HTMLResponse)
def update_registration(request: Request, original_email: str = Form(...), name: str = Form(...), email: str = Form(...), event: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.EventRegistration).filter(models.EventRegistration.email == original_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = name
    user.email = email
    user.event = event
    db.commit()
    return templates.TemplateResponse("sucess.html", {
        "request": request,
        "name": name,
        "email": email,
        "event": event,
        "message": "Update successful!"
    })

@app.post("/delete", response_class=HTMLResponse)
def delete_registration(request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.EventRegistration).filter(models.EventRegistration.email == email).first()
    if user:
        db.delete(user)
        db.commit()
    return templates.TemplateResponse("delete.html", {"request": request, "email": email})
