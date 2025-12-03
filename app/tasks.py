from celery import shared_task
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # Importante para buscar elementos
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
        # --- FASE 1: EXTRACTOR (RPA) ---
        print(f"🌍 Navegando a: {url_to_scrape}")
        driver = get_remote_driver()
        driver.get(url_to_scrape)

        # Obtenemos el título
        title = driver.title

        # Obtenemos el texto del cuerpo (body)
        # Esto extrae todo el texto visible de la página
        body_text = driver.find_element(By.TAG_NAME, "body").text

        # Limpieza básica: Quitamos saltos de línea excesivos
        clean_text = " ".join(body_text.split())

        print(f"✅ Texto extraído ({len(clean_text)} caracteres). Enviando a Gemini...")

        # --- FASE 2: ANALISTA (IA) ---
        analysis = analyze_text_with_gemini(clean_text)

        result_text = f"""
        reporte para: {title}
        --------------------------------
        {analysis}
        """

        print("🧠 Análisis completado:")
        print(result_text)

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return f"Falló: {str(e)}"

    finally:
        if driver:
            driver.quit()

    print(f"🏁 [FIN] Misión cumplida.")
    return result_text
