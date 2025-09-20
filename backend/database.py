from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./resume_check.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # Base is defined here

def create_initial_users():
    from .models import User  # This import is now local to the function

    db = SessionLocal()
    try:
        # Create default admin user if one doesn't exist
        if db.query(User).filter(User.username == "admin").first() is None:
            admin_user = User(username="admin", password="admin123", role="admin")
            db.add(admin_user)
        # Create default user if one doesn't exist
        if db.query(User).filter(User.username == "user").first() is None:
            regular_user = User(username="user", password="user123", role="user")
            db.add(regular_user)
        db.commit()
    except Exception as e:
        print(f"Error creating initial users: {e}")
        db.rollback()
    finally:
        db.close()