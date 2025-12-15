import json
import os
import redis
from celery import shared_task
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from sqlmodel import Session, select
from app.db.session import engine
from app.models.bot import Bot
from app.models.execution import Execution
from app.celery_worker import celery_app
from app.services.ai import analyze_text_with_gemini

# --- CONFIGURACIÓN ---
redis_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
redis_client = redis.from_url(redis_url)


# --- FUNCIONES AUXILIARES (DB) ---
def _start_execution(bot_name: str, url: str):
    """Registra el inicio del trabajo en la BD."""
    with Session(engine) as session:
        bot = session.exec(select(Bot).where(Bot.name == bot_name)).first()
        if not bot:
            return None, None

        # 1. Crear registro de historial
        execution = Execution(
            bot_id=bot.id, status="working", log_text=f"Iniciando tarea en {url}..."
        )
        session.add(execution)

        # 2. Actualizar estado del bot
        bot.status = "working"
        session.add(bot)

        session.commit()
        session.refresh(execution)
        return bot.id, execution.id


def _end_execution(
    bot_id: int,
    execution_id: int,
    status: str,
    log_text: str,
    screenshot_url: str = None,
):
    """Registra el final del trabajo en la BD."""
    if not bot_id or not execution_id:
        return

    with Session(engine) as session:
        # 1. Cerrar historial
        execution = session.get(Execution, execution_id)
        if execution:
            execution.status = status
            execution.finished_at = datetime.utcnow()
            execution.log_text = log_text
            if screenshot_url:
                execution.screenshot_url = screenshot_url
            session.add(execution)

        # 2. Liberar Bot
        bot = session.get(Bot, bot_id)
        if bot:
            bot.status = status
            if status == "completed":
                bot.last_analysis = log_text
                bot.last_analysis_at = datetime.utcnow()
            session.add(bot)

        session.commit()


def _get_driver():
    """Configura Selenium."""
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Remote(command_executor="http://chrome:4444/wd/hub", options=opts)


# --- TAREA PRINCIPAL ---
@celery_app.task(name="run_bot_task")
def run_bot_task(bot_name: str, url_to_scrape: str = "https://www.google.com"):
    print(f"🤖 [START] {bot_name} -> {url_to_scrape}")

    # 1. REGISTRO INICIAL (BD)
    bot_id, execution_id = _start_execution(bot_name, url_to_scrape)
    if not bot_id:
        return "Error: Bot no encontrado"

    driver = None
    status = "completed"
    result_text = ""
    screenshot_url = None

    try:
        # 2. LÓGICA DE NEGOCIO (RPA + IA)
        driver = _get_driver()
        driver.set_window_size(1280, 800)
        driver.get(url_to_scrape)

        raw_text = driver.find_element(By.TAG_NAME, "body").text
        clean_text = " ".join(raw_text.split())[:10000]  # Limpiamos y cortamos

        analysis = analyze_text_with_gemini(clean_text)
        result_text = f"Fuente: {driver.title}\n\n{analysis}"
        if not os.path.exists("media"):
            os.makedirs("media")

        filename = f"exec_{execution_id}.png"
        filepath = os.path.join("media", filename)

        driver.save_screenshot(filepath)
        print(f"📸 Screenshot guardado en: {filepath}")

        # La URL pública será /media/nombre_archivo.png
        screenshot_url = f"/media/{filename}"

    except Exception as e:
        print(f"❌ Error: {e}")
        status = "failed"
        result_text = f"Error en ejecución: {str(e)}"
        if driver:
            try:
                filename = f"error_{execution_id}.png"
                driver.save_screenshot(os.path.join("media", filename))
                screenshot_url = f"/media/{filename}"
            except:
                pass

    finally:
        if driver:
            driver.quit()

    # 3. GUARDADO FINAL (BD)
    _end_execution(bot_id, execution_id, status, result_text, screenshot_url)

    # 4. NOTIFICACIÓN (Redis/WebSockets)
    message = {
        "bot_name": bot_name,
        "status": status,
        "last_analysis": result_text,
        "last_analysis_at": str(datetime.utcnow()),
        "execution_id": execution_id,
    }
    redis_client.publish("bot_updates", json.dumps(message))

    print(f"🏁 [END] {bot_name} finalizado con estado: {status}")
    return result_text
