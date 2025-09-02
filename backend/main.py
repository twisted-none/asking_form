from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any
import re
import os
from datetime import datetime
import telegram_bot
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = FastAPI(
    title="Contact Form API",
    description="API для обработки контактной формы с отправкой в Telegram",
    version="1.0.0"
)

# Настройка CORS - добавляем больше разрешенных источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:80",
        "http://localhost",
        "*"  # В продакшене лучше указать конкретные домены
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Настройки Telegram бота из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(f"🔧 TELEGRAM_BOT_TOKEN: {'✅ Установлен' if TELEGRAM_BOT_TOKEN else '❌ Не установлен'}")
print(f"🔧 TELEGRAM_CHAT_ID: {'✅ Установлен' if TELEGRAM_CHAT_ID else '❌ Не установлен'}")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("⚠️ ВНИМАНИЕ: Telegram бот не настроен. Установите переменные окружения TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID")

# Модель для формы с вопросами/ответами
class QuestionForm(BaseModel):
    question1: str
    answer1: str
    question2: str
    answer2: str
    question3: str
    answer3: str

    @field_validator('question1', 'question2', 'question3', 'answer1', 'answer2', 'answer3')
    @classmethod
    def validate_fields(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Поле обязательно для заполнения')
        if len(v.strip()) < 2:
            raise ValueError('Минимум 2 символа')
        return v.strip()

@app.get("/")
async def root():
    return {"message": "Contact Form API работает!", "status": "ok"}

@app.post("/submit-questions")
async def submit_questions(form_data: QuestionForm):
    """Эндпоинт для отправки формы с вопросами/ответами"""
    try:
        print(f"📝 Получены данные вопросов: {form_data}")
        
        # Отправляем в Telegram если бот настроен
        telegram_success = {"message_sent": False, "excel_sent": False}
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            print("📤 Отправляем данные в Telegram...")
            telegram_success = await telegram_bot.send_form_data(
                TELEGRAM_BOT_TOKEN, 
                TELEGRAM_CHAT_ID, 
                form_data.model_dump()
            )
            print(f"✅ Результат отправки: {telegram_success}")
        else:
            print("⚠️ Telegram бот не настроен")
        
        return {
            "status": "success",
            "message": "Форма с вопросами успешно отправлена!",
            "telegram_status": telegram_success,
            "data": form_data.model_dump()
        }
    except Exception as e:
        print(f"❌ Ошибка при обработке формы: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "Сервер работает нормально",
        "telegram_configured": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)