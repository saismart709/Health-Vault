from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import engine, Base
from .routes import auth, dashboard, vitals, medications, emergency
import os
from .config import BASE_DIR

app = FastAPI(title="HealthVault AI")

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "app", "static")), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(vitals.router)
app.include_router(medications.router)
app.include_router(emergency.router, prefix="/emergency", tags=["Emergency"])

@app.on_event("startup")
async def startup():
    # Initialize database - protected for read-only environments
    try:
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all) # Refresh for report analysis fields
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Database initialization skipped or failed: {e}")
        return
    
    # Create demo user if not exists
    from .database import SessionLocal
    from .models import User
    from .auth import get_password_hash
    from sqlalchemy.future import select
    
    async with SessionLocal() as db:
        result = await db.execute(select(User).where(User.username == "patient_demo"))
        if not result.scalars().first():
            demo_user = User(
                username="patient_demo",
                email="demo@example.com",
                hashed_password=get_password_hash("password123"),
                full_name="John Doe",
                role="patient",
                age=65,
                gender="male",
                blood_group="O+",
                phone="+1-555-0101",
                address="123 Health Ave, Medical City",
                allergies="Peanuts, Penicillin",
                chronic_diseases="Type 2 Diabetes, Hypertension"
            )
            db.add(demo_user)
            await db.flush() # Get user ID
            
            # Add demo contact
            from .models import EmergencyContact, Medication, Vital
            from datetime import datetime
            
            contact = EmergencyContact(
                user_id=demo_user.id,
                name="Jane Doe",
                phone="+1-555-0199",
                email="jane@example.com",
                relationship_type="Spouse"
            )
            db.add(contact)
            
            # Add demo meds
            med1 = Medication(user_id=demo_user.id, name="Metformin", dosage="500mg", frequency="Daily", duration="Chronic")
            med2 = Medication(user_id=demo_user.id, name="Lisinopril", dosage="10mg", frequency="Daily", duration="Chronic")
            db.add_all([med1, med2])
            
            # Add demo vital
            vital = Vital(user_id=demo_user.id, heart_rate=82, blood_pressure_sys=145, blood_pressure_dia=92, blood_sugar=180, temperature=98.6)
            db.add(vital)
            
            await db.commit()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
