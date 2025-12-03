import os
import google.generativeai as genai

# Configuramos la IA al cargar el archivo
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


def analyze_text_with_gemini(text: str) -> str:
    """
    Recibe un texto largo y le pide a Gemini un resumen.
    """
    if not api_key:
        return "⚠️ Error: No se configuró la API Key de Gemini."

    try:
        model_name = "gemini-2.0-flash"
        model = genai.GenerativeModel(model_name)

        prompt = f"""
        Actúa como un analista experto. Analiza el siguiente texto extraído de una página web:
        
        "{text[:8000]}"  # Cortamos a 8000 caracteres para no exceder límites gratis
        
        Por favor entrega:
        1. Un resumen de 3 puntos clave.
        2. El sentimiento general (Positivo/Negativo/Neutral).
        3. Una frase de conclusión.
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        # --- BLOQUE DE DIAGNÓSTICO ---
        print(f"❌ Error usando el modelo '{model_name}': {e}")
        print("🔍 LISTANDO MODELOS DISPONIBLES PARA TU API KEY:")
        try:
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    print(f"   👉 {m.name}")
        except Exception as list_error:
            print(f"   No se pudieron listar los modelos: {list_error}")
        # -----------------------------

        return (
            f"Error IA: {str(e)}. Revisa los logs del worker para ver modelos válidos."
        )
