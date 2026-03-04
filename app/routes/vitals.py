from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from ..database import get_db
from ..models import Vital
from .dashboard import get_current_user_from_cookie
from fastapi.templating import Jinja2Templates

from ..config import BASE_DIR
import os

router = APIRouter(prefix="/vitals")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))

@router.get("/")
async def vitals_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    result = await db.execute(select(Vital).where(Vital.user_id == user.id).order_by(desc(Vital.timestamp)))
    vitals = result.scalars().all()
    return templates.TemplateResponse("vitals.html", {"request": request, "vitals": vitals})

@router.post("/add")
async def add_vital(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    form_data = await request.form()
    
    # Robust numeric parsing
    def safe_float(val, default=0.0):
        try:
            return float(val) if val else default
        except (ValueError, TypeError):
            return default

    heart_rate = safe_float(form_data.get("heart_rate"))
    blood_pressure_sys = safe_float(form_data.get("blood_pressure_sys"))
    blood_pressure_dia = safe_float(form_data.get("blood_pressure_dia"))
    blood_sugar = safe_float(form_data.get("blood_sugar"))
    temperature = safe_float(form_data.get("temperature"))
    
    # Prepare data for analysis BEFORE commit (to avoid MissingGreenlet error)
    user_info = {
        "age": user.age or 30,
        "conditions": user.chronic_diseases or ""
    }
    vital_dict = {
        "heart_rate": heart_rate,
        "blood_pressure_sys": blood_pressure_sys,
        "blood_pressure_dia": blood_pressure_dia,
        "blood_sugar": blood_sugar,
        "temperature": temperature
    }

    new_vital = Vital(
        user_id=user.id,
        heart_rate=heart_rate,
        blood_pressure_sys=blood_pressure_sys,
        blood_pressure_dia=blood_pressure_dia,
        blood_sugar=blood_sugar,
        temperature=temperature
    )
    db.add(new_vital)
    await db.commit()
    
    # Trigger High-Risk Analysis and Notification
    from ..ai_engine import ai_engine
    
    analysis = ai_engine.analyze_vitals(user_info, vital_dict)
    
    if analysis['risk_level'] == "High":
        # Redirect toward emergency workflow
        return RedirectResponse(url="/emergency?alert=true", status_code=303)
        
    return RedirectResponse(url="/vitals", status_code=303)

