from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Column, Float, String, Integer

app = FastAPI()

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

class SensorValueDB(Base):
    __tablename__ = 'sensor_values'

    id = Column(Integer, primary_key=True, index=True)
    facts = Column(String, nullable = True)
    MQ2_value = Column(Float)
    MQ7_value = Column(Float)

Base.metadata.create_all(bind=engine)

class SensorValue(BaseModel):
    facts: str
    MQ2_value: float
    MQ7_value: float

    class Config:
        orm_mode = True

# def get_sensor_value(db: Session, sensor_id: int):
#     return db.query(SensorValueDB).where(SensorValueDB.id == sensor_id).first()

def get_sensor_values(db: Session):
    return db.query(SensorValueDB).order_by(SensorValueDB.id.desc()).limit(3).all()

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

# @app.get('/values/{value_id}')
# def get_value_endpoint(value_id: int, db: Session = Depends(get_db)):
#     return get_sensor_value(db, value_id)

@app.get('/')
async def root():
    return {'message': 'Hello World!'}
