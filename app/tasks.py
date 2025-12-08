from celery import shared_task
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # Importante para buscar elementos

# --- IMPORTS DE BASE DE DATOS ---
from sqlmodel import Session, select
from app.db.session import engine  # Necesitamos el motor para crear una sesión
from app.models.bot import Bot  # Necesitamos el modelo para buscar y actualizar

# --------------------------------
from app.celery_worker import celery_app
from app.services.ai import analyze_text_with_gemini  # Importamos nuestro cerebro


def get_remote_driver():
    """Configura la conexión con Selenium Grid"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Remote(
        command_executor="http://chrome:4444/wd/hub", options=chrome_options
    )
    return driver


@celery_app.task(name="run_bot_task")
def run_bot_task(bot_name: str, url_to_scrape: str = "https://www.google.com"):
    print(f"🤖 [INICIO] El bot '{bot_name}' inicia su misión de inteligencia...")

    driver = None
    result_text = ""

    try:
        print("🔍 Iniciando proceso de scraping..." + datetime.utcnow())
        # 1. RPA
        driver = get_remote_driver()
        print(f"🌍 Navegando a: {url_to_scrape}")
        driver.get(url_to_scrape)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        clean_text = " ".join(body_text.split())  # Limpiar espacios

        # 2. IA
        print("🧠 Enviando a Gemini...")
        analysis = analyze_text_with_gemini(clean_text)

        result_text = f"Fuente: {driver.title}\n\n{analysis}"

        # 3. PERSISTENCIA (GUARDAR EN DB)
        # Abrimos una sesión efímera solo para guardar esto
        with Session(engine) as session:
            # Buscamos el bot por nombre
            statement = select(Bot).where(Bot.name == bot_name)
            bot_db = session.exec(statement).first()

            if bot_db:
                bot_db.last_analysis = result_text  # <--- GUARDAMOS AQUÍ
                bot_db.last_analysis_at = datetime.utcnow()
                bot_db.status = "completed"
                session.add(bot_db)
                session.commit()
                print("💾 Análisis guardado en base de datos.")
            else:
                print("⚠️ No encontré el bot en la BD para guardar el resultado.")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return f"Falló: {str(e)}"

    finally:
        if driver:
            driver.quit()

    print(f"🏁 [FIN] Misión cumplida.")
    return result_text
