from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from ..models import EmergencyContact, User, Vital, Medication, HealthNotification
from .dashboard import get_current_user_from_cookie
from fastapi.templating import Jinja2Templates
import random

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def emergency_page(request: Request, alert: bool = False, db: AsyncSession = Depends(get_db)):
    print("DEBUG: /emergency/ GET hit")
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    result = await db.execute(select(EmergencyContact).where(EmergencyContact.user_id == user.id))
    contacts = result.scalars().all()
    return templates.TemplateResponse("emergency.html", {
        "request": request, 
        "user": user,
        "contacts_list": contacts,
        "alert_sent": False,
        "is_high_risk": alert
    })

@router.post("/trigger")
async def trigger_emergency(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    # Simulate Live Location
    lat = 37.7749 + (random.random() - 0.5) * 0.01
    lon = -122.4194 + (random.random() - 0.5) * 0.01
    
    # Fetch data to "send"
    contacts_result = await db.execute(select(EmergencyContact).where(EmergencyContact.user_id == user.id))
    contacts = contacts_result.scalars().all()
    
    contacts_str = ", ".join([c.name for c in contacts])
    
    return templates.TemplateResponse("emergency.html", {
        "request": request,
        "user": user,
        "contacts_list": contacts,
        "alert_sent": True,
        "contacts": contacts_str,
        "location": {"lat": round(lat, 4), "lon": round(lon, 4)}
    })

@router.post("/add-contact")
async def add_emergency_contact(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    print("DEBUG: /emergency/add-contact POST hit")
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    try:
        form = await request.form()
        name = form.get("name")
        phone = form.get("phone")
        relationship = form.get("relationship")
        email = form.get("email")
        is_high_risk = form.get("is_high_risk", "False")
        
        print(f"DEBUG: Adding contact for user {user.id}: {name}, is_high_risk={is_high_risk}")
        
        new_contact = EmergencyContact(
            user_id=user.id,
            name=name,
            phone=phone,
            relationship_type=relationship,
            email=email
        )
        db.add(new_contact)
        
        if is_high_risk.lower() == "true":
            notification = HealthNotification(
                user_id=user.id,
                message=f"CRITICAL ALERT: Emergency contact {name} added during a high health risk event. Notification has been sent to them.",
                type="HighRisk",
                priority="Urgent",
                family_notified=True
            )
            db.add(notification)
        
        await db.commit()
        
        redirect_url = "/emergency"
        if is_high_risk.lower() == "true":
            redirect_url += "?alert=true&contact_added=true"
            
        return RedirectResponse(url=redirect_url, status_code=303)
    except Exception as e:
        print(f"DEBUG: Error in add_emergency_contact: {e}")
        return RedirectResponse(url="/emergency?error=submission_failed", status_code=303)
