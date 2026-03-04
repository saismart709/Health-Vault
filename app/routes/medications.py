from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from ..models import Medication
from .dashboard import get_current_user_from_cookie
from fastapi.templating import Jinja2Templates

from ..main import BASE_DIR
import os

router = APIRouter(prefix="/medications")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))

@router.get("/")
async def medications_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    result = await db.execute(select(Medication).where(Medication.user_id == user.id))
    medications = result.scalars().all()
    return templates.TemplateResponse("medications.html", {"request": request, "medications": medications})

@router.post("/add")
async def add_medication(
    request: Request,
    name: str = Form(...),
    dosage: str = Form(...),
    frequency: str = Form(...),
    duration: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    new_med = Medication(
        user_id=user.id,
        name=name,
        dosage=dosage,
        frequency=frequency,
        duration=duration
    )
    db.add(new_med)
    await db.commit()
    return RedirectResponse(url="/medications", status_code=303)

@router.get("/delete/{med_id}")
async def delete_medication(request: Request, med_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    result = await db.execute(select(Medication).where(Medication.id == med_id, Medication.user_id == user.id))
    med = result.scalars().first()
    if med:
        await db.delete(med)
        await db.commit()
    return RedirectResponse(url="/medications", status_code=303)
