"""
Seed script to create or update the admin user.
Run with the project's Python (inside the venv):
    .\venv\Scripts\python seed_admin.py
"""

from database import sync_engine
from sqlalchemy.orm import sessionmaker
from models import Staff
from auth import get_password_hash

SessionLocal = sessionmaker(bind=sync_engine)

def main():
    db = SessionLocal()
    try:
        existing = db.query(Staff).filter(Staff.email == "admin@lbca.edu.ph").first()

        if existing:
            existing.password_hash = get_password_hash("Admin123!")
            db.commit()
            print("Admin already existed — password hash refreshed.")
        else:
            admin = Staff(
                email="admin@lbca.edu.ph",
                password_hash=get_password_hash("Admin123!"),
                first_name="System",
                last_name="Administrator",
                contact_number="+639123456789",
                role="admin",
                account_status="approved",
                is_approved=True,
                requires_password_change=False,
            )
            db.add(admin)
            db.commit()
            print("Admin created: admin@lbca.edu.ph / Admin123!")
    finally:
        db.close()

if __name__ == '__main__':
    main()
