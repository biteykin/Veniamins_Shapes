from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Подключение к БД на Railway
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:RiFCVtQKPvaTSqFqGKxDUJtlCVfRanql@postgres.railway.internal:5432/railway")

# Создаем движок для работы с базой данных
engine = create_engine(DATABASE_URL)

# Создаем сессию для работы с базой данных
SessionLocal = sessionmaker(bind=engine)

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Определяем модель рейтингов
class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    min_score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    result_text = Column(String, nullable=False)

# Создаем таблицы в базе данных (если их нет)
Base.metadata.create_all(bind=engine)

# Создаем экземпляр FastAPI
app = FastAPI()

# Эндпоинт для проверки работоспособности сервера
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Эндпоинт для получения рейтинга по количеству очков
@app.get("/rating/{score}")
def get_rating(score: int):
    # Создаем сессию для работы с базой данных
    session = SessionLocal()

    # Ищем рейтинг, который соответствует переданному количеству очков
    rating = session.query(Rating).filter(Rating.min_score <= score, Rating.max_score >= score).first()

    # Закрываем сессию
    session.close()

    # Если рейтинг не найден, возвращаем ошибку 404
    if not rating:
        raise HTTPException(status_code=404, detail="Рейтинг не найден")

    # Возвращаем результат
    return {"score": score, "result": rating.result_text}

# Эндпоинт для добавления нового рейтинга
@app.post("/rating")
def add_rating(min_score: int, max_score: int, result_text: str):
    # Создаем сессию для работы с базой данных
    session = SessionLocal()

    # Создаем новый объект рейтинга
    new_rating = Rating(min_score=min_score, max_score=max_score, result_text=result_text)

    # Добавляем объект в сессию
    session.add(new_rating)

    # Сохраняем изменения в базе данных
    session.commit()

    # Закрываем сессию
    session.close()

    # Возвращаем сообщение об успешном добавлении
    return {"message": "Рейтинг успешно добавлен", "id": new_rating.id}

# Эндпоинт для получения всех рейтингов
@app.get("/ratings")
def get_all_ratings():
    # Создаем сессию для работы с базой данных
    session = SessionLocal()

    # Получаем все рейтинги из базы данных
    ratings = session.query(Rating).all()

    # Закрываем сессию
    session.close()

    # Возвращаем список рейтингов
    return {"ratings": [{"id": r.id, "min_score": r.min_score, "max_score": r.max_score, "result_text": r.result_text} for r in ratings]}

# Эндпоинт для удаления рейтинга по ID
@app.delete("/rating/{rating_id}")
def delete_rating(rating_id: int):
    # Создаем сессию для работы с базой данных
    session = SessionLocal()

    # Ищем рейтинг по ID
    rating = session.query(Rating).filter(Rating.id == rating_id).first()

    # Если рейтинг не найден, возвращаем ошибку 404
    if not rating:
        session.close()
        raise HTTPException(status_code=404, detail="Рейтинг не найден")

    # Удаляем рейтинг из базы данных
    session.delete(rating)

    # Сохраняем изменения в базе данных
    session.commit()

    # Закрываем сессию
    session.close()

    # Возвращаем сообщение об успешном удалении
    return {"message": "Рейтинг успешно удален", "id": rating_id}
