from celery import shared_task  # Nota: Usar shared_task es más limpio en versiones modernas
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from app.celery_worker import celery_app


def get_remote_driver():
    """Configura la conexión con el contenedor de Chrome"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # No necesitamos ver la UI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Nos conectamos al servicio 'chrome' que definimos en docker-compose
    # El puerto 4444 es donde escucha Selenium Grid
    driver = webdriver.Remote(
        command_executor="http://chrome:4444/wd/hub", options=chrome_options
    )
    return driver


@celery_app.task(name="run_bot_task")
def run_bot_task(bot_name: str, url_to_scrape: str = "https://www.python.org"):
    print(f"🤖 [INICIO] El bot '{bot_name}' está encendiendo motores...")
    driver = None
    title = "Error"

    try:
        # 1. Iniciamos el navegador remoto
        print("📡 Conectando con el navegador remoto...")
        driver = get_remote_driver()

        # 2. Navegamos
        print(f"🌍 Navegando a: {url_to_scrape}")
        driver.get(url_to_scrape)

        # 3. Extraemos datos (RPA Básico)
        title = driver.title
        print(f"✅ Título encontrado: {title}")

        # (Aquí guardarías el resultado en la BD si quisieras)

    except Exception as e:
        print(f"❌ Error en el bot: {e}")
        return f"Falló: {str(e)}"

    finally:
        # 4. Limpieza (Muy importante cerrar la sesión)
        if driver:
            driver.quit()

    print(f"🏁 [FIN] El bot terminó.")
    return f"Bot '{bot_name}' visitó {url_to_scrape} | Título: {title}"
