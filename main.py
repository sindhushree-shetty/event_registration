from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
from fastapi import HTTPException


app = FastAPI()

# Mount static folder for CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates folder
templates = Jinja2Templates(directory="templates")

# Login page
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# After login, show registration form
@app.post("/login", response_class=HTMLResponse)
def login(request: Request, email: str = Form(...)):
    return templates.TemplateResponse("register.html", {"request": request, "email": email})

# Save registration data
@app.post("/register", response_class=HTMLResponse)
def register(request: Request, name: str = Form(...), email: str = Form(...), event: str = Form(...)):
    new_data = {"name": name, "email": email, "event": event}

    # Create the data.json file if it doesn't exist
    if not os.path.exists("data.json"):
        with open("data.json", "w") as f:
            json.dump([], f)

    # Load existing registrations
    with open("data.json", "r") as f:
        data = json.load(f)

    # ✅ Check if email already exists
    for participant in data:
        if participant["email"] == email:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "message": "Email already registered!"
            })

    # Add new registration
    data.append(new_data)

    # Save the updated data
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

    return templates.TemplateResponse("sucess.html", {
        "request": request,
        "name": name,
        "event": event,
        "email": email
    })




# Show update form with old values
@app.post("/update-page", response_class=HTMLResponse)
def show_update_page(request: Request, email: str = Form(...)):
    with open("data.json", "r") as f:
        data = json.load(f)

    # Find user data by email
    for participant in data:
        if participant["email"] == email:
            return templates.TemplateResponse("update.html", {
                "request": request,
                "name": participant["name"],
                "email": participant["email"],
                "event": participant["event"]
            })

    raise HTTPException(status_code=404, detail="User not found")    # If not found


# This will handle update form submission
@app.post("/update", response_class=HTMLResponse)
def update_registration(request: Request, original_email: str = Form(...), name: str = Form(...), email: str = Form(...), event: str = Form(...)):
    with open("data.json", "r") as f:
        data = json.load(f)

    # Find and update user
    for participant in data:
        if participant["email"] == original_email:
            participant["name"] = name
            participant["email"] = email
            participant["event"] = event
            break

  # Save updated data
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)
    return templates.TemplateResponse("sucess.html", {
        "request": request,
        "name": name,
        "email": email,
        "event": event,
        "message": "Update successful!"
    })

# ✅ Delete registration
@app.post("/delete", response_class=HTMLResponse)
def delete_registration(request: Request, email: str = Form(...)):
    with open("data.json", "r") as f:
        data = json.load(f)
 
   # Remove the matching user
    updated_data = [participant for participant in data if participant["email"] != email]

   # Save new data
    with open("data.json", "w") as f:
        json.dump(updated_data, f, indent=4)

    return templates.TemplateResponse("delete.html", {
        "request": request,
        "email": email
    })

