from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Column, Float, String, Integer

app = FastAPI()

# Allow CORS for requests from certain origins

origins = [
    "http://localhost",
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Establish connection with SQLite

SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./db.sqlite3:'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create Table

class SensorValueDB(Base):
    __tablename__ = 'sensor_values'

    id = Column(Integer, primary_key=True, index=True)
    facts = Column(String, nullable = True)
    MQ2_value = Column(Float)
    MQ7_value = Column(Float)

Base.metadata.create_all(bind=engine)

# Pydantic class - For validation 

class SensorValue(BaseModel):
    facts: str
    MQ2_value: float
    MQ7_value: float

    class Config:
        orm_mode = True

def get_sensor_values(db: Session):
    return db.query(SensorValueDB).order_by(SensorValueDB.id.desc()).limit(15).all()

def create_sensor_value(db: Session, sensorValue: SensorValue):
    db_value = SensorValueDB(**sensorValue.dict())
    db.add(db_value)
    db.commit()
    db.refresh(db_value)

    return db_value

# Routes for interacting with the API

@app.post('/values/', response_model=SensorValue)
def create_values_endpoint(sensorValue: SensorValue, db: Session = Depends(get_db)):
    db_value = create_sensor_value(db, sensorValue)
    return db_value

@app.get('/values/', response_model=List[SensorValue])
def get_values_endpoint(db: Session = Depends(get_db)):
    return get_sensor_values(db)

@app.get('/values/{value_id}')
def get_value_endpoint(value_id: int, db: Session = Depends(get_db)):
    return get_sensor_value(db, value_id)

@app.get('/')
async def root():
    return {'message': 'Hello World!'}
