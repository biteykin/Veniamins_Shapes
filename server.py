from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Подключение к БД на Railway
DATABASE_URL = os.getenv("DATABASE_URL", "monorail.proxy.rlwy.net:58544")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Определяем модель рейтингов
class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    min_score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    result_text = Column(String, nullable=False)

# Создаём таблицы (если их нет)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Получение рейтинга по количеству очков
@app.get("/rating/{score}")
def get_rating(score: int):
    session = SessionLocal()
    rating = session.query(Rating).filter(Rating.min_score <= score, Rating.max_score >= score).first()
    session.close()
    if not rating:
        raise HTTPException(status_code=404, detail="Рейтинг не найден")
    return {"score": score, "result": rating.result_text}
