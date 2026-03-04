from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String)  # patient, caregiver, doctor, emergency_contact
    
    # Profile info
    age = Column(Integer)
    gender = Column(String)
    blood_group = Column(String)
    phone = Column(String)
    address = Column(Text)
    allergies = Column(Text)
    chronic_diseases = Column(Text)
    
    vitals = relationship("Vital", back_populates="user")
    medical_records = relationship("MedicalRecord", back_populates="user")
    medications = relationship("Medication", back_populates="user")
    emergency_contacts = relationship("EmergencyContact", back_populates="user")
    notifications = relationship("HealthNotification", back_populates="user")

class Vital(Base):
    __tablename__ = "vitals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    heart_rate = Column(Float)
    blood_pressure_sys = Column(Float)
    blood_pressure_dia = Column(Float)
    blood_sugar = Column(Float)
    temperature = Column(Float)
    
    user = relationship("User", back_populates="vitals")

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text)
    file_path = Column(String)
    analysis_result = Column(Text)
    health_status = Column(String) # Stable, Critical, Needs Attention etc.
    date_uploaded = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="medical_records")

class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    dosage = Column(String)
    frequency = Column(String)  # daily, twice_daily, etc.
    duration = Column(String)
    start_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="medications")
    reminders = relationship("MedicationReminder", back_populates="medication")

class MedicationReminder(Base):
    __tablename__ = "medication_reminders"
    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"))
    scheduled_time = Column(DateTime)
    is_taken = Column(Boolean, default=False)
    
    medication = relationship("Medication", back_populates="reminders")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    relationship_type = Column(String)
    
    user = relationship("User", back_populates="emergency_contacts")

class HealthNotification(Base):
    __tablename__ = "health_notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    type = Column(String) # 'HighRisk', 'Medication', etc.
    priority = Column(String) # 'Urgent', 'Normal'
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    family_notified = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="notifications")
