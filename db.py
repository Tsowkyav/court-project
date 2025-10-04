from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session

SQLITE_URL = "sqlite:///./court_data.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD functions
def save_query(db: Session, case_type: str, case_number: str, year: str, result: str):
    from .models import Query
    query = Query(case_type=case_type, case_number=case_number, year=year, result=result)
    db.add(query)
    db.commit()
    db.refresh(query)
    return query

def get_query(db: Session, query_id: int):
    from .models import Query
    return db.query(Query).filter(Query.id == query_id).first()
