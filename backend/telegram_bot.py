import asyncio
import logging
from typing import Dict, Any
import pandas as pd
from io import BytesIO
import os
from datetime import datetime
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_message(bot: Bot, chat_id: str, text: str) -> bool:
    """Отправка текстового сообщения"""
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        logger.info("✅ Сообщение успешно отправлено")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке сообщения: {e}")
        return False

async def send_document(bot: Bot, chat_id: str, file_bytes: bytes, filename: str, caption: str = "") -> bool:
    """Отправка документа"""
    try:
        document = BufferedInputFile(file_bytes, filename=filename)
        await bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption
        )
        logger.info(f"✅ Документ {filename} успешно отправлен")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке документа: {e}")
        return False

def create_excel_file(form_data: Dict[str, Any]) -> bytes:
    """Создание Excel файла из данных формы с вопросами/ответами"""
    logger.info("📊 Создание Excel файла...")
    
    # Подготавливаем данные для Excel
    data = []
    
    for i in range(1, 4):
        question_key = f'question{i}'
        answer_key = f'answer{i}'
        if form_data.get(question_key) and form_data.get(answer_key):
            data.append({
                'Номер вопроса': i,
                'Вопрос': form_data[question_key],
                'Ответ': form_data[answer_key],
                'Дата отправки': datetime.now().strftime('%d.%m.%Y %H:%M')
            })
    
    # Создаем DataFrame и Excel файл
    df = pd.DataFrame(data)
    
    # Создаем Excel в памяти
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Данные формы')
        
        # Автоматическая настройка ширины колонок
        worksheet = writer.sheets['Данные формы']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    excel_buffer.seek(0)
    logger.info("✅ Excel файл создан успешно")
    return excel_buffer.getvalue()

def format_message(form_data: Dict[str, Any]) -> str:
    """Форматирование данных формы в текстовое сообщение"""
    timestamp = datetime.now().strftime('%d.%m.%Y в %H:%M')
    
    message = f"📝 <b>Новая форма с вопросами</b>\n"
    message += f"🕐 Отправлено: {timestamp}\n\n"
    
    for i in range(1, 4):
        question_key = f'question{i}'
        answer_key = f'answer{i}'
        if form_data.get(question_key) and form_data.get(answer_key):
            message += f"❓ <b>Вопрос {i}:</b>\n{form_data[question_key]}\n\n"
            message += f"✅ <b>Ответ {i}:</b>\n{form_data[answer_key]}\n\n"
            message += "─────────────────\n\n"
    
    return message

async def send_form_data(bot_token: str, chat_id: str, form_data: Dict[str, Any]) -> Dict[str, bool]:
    """Отправка данных формы (сообщение + Excel файл)"""
    logger.info(f"📤 Начинаем отправку данных в чат {chat_id}")
    
    # Создаем бота
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    results = {
        "message_sent": False,
        "excel_sent": False
    }
    
    try:
        # Отправляем текстовое сообщение
        logger.info("📨 Отправляем текстовое сообщение...")
        message_text = format_message(form_data)
        results["message_sent"] = await send_message(bot, chat_id, message_text)
        
        # Создаем и отправляем Excel файл
        logger.info("📊 Создаем и отправляем Excel файл...")
        try:
            excel_bytes = create_excel_file(form_data)
            filename = f"form_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            caption = "📊 Данные формы в формате Excel"
            results["excel_sent"] = await send_document(bot, chat_id, excel_bytes, filename, caption)
        except Exception as e:
            logger.error(f"❌ Ошибка создания Excel файла: {e}")
        
        logger.info(f"📋 Результат отправки: {results}")
        return results
    
    except Exception as e:
        logger.error(f"❌ Общая ошибка при отправке: {e}")
        return results
    
    finally:
        # Закрываем сессию бота
        try:
            await bot.session.close()
            logger.info("🔐 Сессия бота закрыта")
        except:
            pass

async def test_bot_connection(bot_token: str) -> bool:
    """Тестирование подключения к боту"""
    bot = Bot(token=bot_token)
    
    try:
        me = await bot.get_me()
        logger.info(f"✅ Бот подключен: @{me.username} ({me.first_name})")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к боту: {e}")
        return False
    finally:
        try:
            await bot.session.close()
        except:
            pass

# Функция для быстрой отправки тестового сообщения
async def send_test_message(bot_token: str, chat_id: str, message: str = "🧪 Тестовое сообщение") -> bool:
    """Отправка тестового сообщения"""
    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info("✅ Тестовое сообщение отправлено")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка отправки тестового сообщения: {e}")
        return False
    finally:
        try:
            await bot.session.close()
        except:
            pass