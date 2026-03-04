from fastapi import APIRouter, Depends, Request, status, Form, UploadFile, File
import shutil
import os
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from ..database import get_db
from ..models import User, Vital, Medication
from ..auth import get_current_user
from ..ai_engine import ai_engine
from typing import Optional

from ..config import BASE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))

async def get_current_user_from_cookie(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        return None
    token = token.split(" ")[1]
    from ..auth import get_current_user
    try:
        return await get_current_user(token, db)
    except:
        return None

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    # Fetch recent vitals
    vitals_result = await db.execute(select(Vital).where(Vital.user_id == user.id).order_by(desc(Vital.timestamp)).limit(5))
    vitals = vitals_result.scalars().all()
    
    # Fetch medications
    meds_result = await db.execute(select(Medication).where(Medication.user_id == user.id, Medication.is_active == True))
    medications = meds_result.scalars().all()
    
    # Latest Report Status
    from ..models import MedicalRecord
    report_result = await db.execute(select(MedicalRecord).where(MedicalRecord.user_id == user.id).order_by(desc(MedicalRecord.date_uploaded)).limit(1))
    latest_report = report_result.scalars().first()
    
    # AI Analysis
    risk = {"risk_score": 0, "risk_level": "Low", "reasons": ["No vital data yet"], "action": "Please add vitals"}
    if vitals:
        latest = vitals[0]
        vital_dict = {
            "heart_rate": latest.heart_rate,
            "blood_pressure_sys": latest.blood_pressure_sys,
            "blood_pressure_dia": latest.blood_pressure_dia,
            "blood_sugar": latest.blood_sugar,
            "temperature": latest.temperature
        }
        user_info = {
            "age": user.age or 30,
            "conditions": user.chronic_diseases or ""
        }
        risk = ai_engine.analyze_vitals(user_info, vital_dict)
    
    # Fetch Notifications
    from ..models import HealthNotification
    notif_result = await db.execute(
        select(HealthNotification)
        .where(HealthNotification.user_id == user.id)
        .order_by(desc(HealthNotification.timestamp))
        .limit(3)
    )
    notifications = notif_result.scalars().all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "vitals": vitals,
        "medications": medications,
        "risk": risk,
        "latest_report": latest_report,
        "notifications": notifications
    })

@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    from ..models import MedicalRecord
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.user_id == user.id))
    records = result.scalars().all()
    
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "user": user,
        "medical_records": records
    })

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user
    })

@router.post("/profile/update")
async def update_profile(
    request: Request,
    full_name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    user.full_name = full_name
    user.age = age
    user.gender = gender
    user.phone = phone
    user.address = address
    
    await db.commit()
    return RedirectResponse(url="/profile", status_code=303)

@router.post("/reports/upload")
async def upload_report(
    request: Request,
    title: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    # Save file
    upload_dir = os.path.join(BASE_DIR, "app", "static", "uploads")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # AI Analysis
    analysis = ai_engine.analyze_medical_report(file.filename)
    
    from ..models import MedicalRecord
    new_record = MedicalRecord(
        user_id=user.id,
        title=title,
        file_path=f"/static/uploads/{file.filename}",
        analysis_result=analysis['analysis'],
        health_status=analysis['status']
    )
    db.add(new_record)
    await db.commit()
    
    return RedirectResponse(url="/reports", status_code=303)

@router.get("/reports/delete/{report_id}")
async def delete_report(
    report_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    from ..models import MedicalRecord
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == report_id, MedicalRecord.user_id == user.id))
    report = result.scalars().first()
    
    if report:
        # Delete file
        try:
            full_path = f"app{report.file_path}"
            if os.path.exists(full_path):
                os.remove(full_path)
        except:
            pass
            
        await db.delete(report)
        await db.commit()
        
    return RedirectResponse(url="/reports", status_code=303)
@router.get("/profile/delete")
async def delete_profile(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    # Delete user (cascading deletes should handle relations if configured, 
    # but let's be safe or just delete the user record)
    await db.delete(user)
    await db.commit()
    
    response = RedirectResponse(url="/login?msg=account_deleted", status_code=303)
    response.delete_cookie("access_token")
    return response
