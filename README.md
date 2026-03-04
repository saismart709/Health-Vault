# HealthVault AI - Smart Health Record & Emergency System

A secure, Python-based digital health system for managing medical records, risk detection, and emergency alerts.

## Features
- **Centralized Health Records**: Store and track medical history.
- **AI Risk Analysis**: Real-time analysis of vitals (HP, BP, Sugar, Temp) using thresholds and ML-based patterns.
- **Medication Management**: Track daily doses and schedules.
- **Emergency Alert System**: One-click emergency trigger with simulated live location tracking.
- **Security**: Password hashing, JWT session-based security, and role-based access.

## Tech Stack
- **Backend**: Python, FastAPI
- **Database**: SQLite with SQLAlchemy (Asynchronous)
- **AI/ML**: Pandas, Scikit-Learn (Threshold & trend analysis)
- **Frontend**: Jinja2 Templates + Vanilla CSS (Premium Dark Theme)

## Getting Started

### Prerequisites
- Python 3.9+
- Virtual Environment (recommended)

### Installation
1. Clone the repository or navigate to the folder.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
1. Start the server:
   ```bash
   python main.py
   ```
2. Open your browser at: `http://127.0.0.1:8000`

### Demo Credentials
- **Username**: `patient_demo`
- **Password**: `password123`

## Implementation Detail
- **Security**: Implemented using `passlib` for hashing and `jose` for JWT tokens stored in HTTP-only cookies.
- **AI Engine**: Uses a rule-based hybrid model to detect risks in vital signs and provide explainable alerts.
- **Database**: Asynchronous SQLite ensures high performance and concurrency support.
