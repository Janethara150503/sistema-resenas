import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Asegura que OPENAI_API_KEY esté disponible aunque este módulo se importe
# antes de que app.py ejecute load_dotenv()
load_dotenv()

# El prompt se construye con los datos reales del catálogo
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres un asistente cálido para un catálogo personal de reseñas de "
        "películas, libros y restaurantes. Responde en español, en máximo 3 "
        "oraciones, usando SOLO los datos que se te dan. No inventes títulos "
        "ni cifras.",
    ),
    (
        "human",
        "Datos del catálogo:\n"
        "- Total de reseñas: {total} ({sin_calificar} sin calificación)\n"
        "- Calificación promedio: {promedio}\n"
        "- Reseñas por tipo: {por_tipo}\n"
        "- Mejor calificada: {mejor}\n"
        "- Peor calificada: {peor}\n\n"
        "Tono del mensaje: {tono}\n"
        "Escribe un resumen breve del estado del catálogo.",
    ),
])

_chain = None


def _get_chain():
    """Crea el modelo la primera vez que se necesita (así un error de
    configuración no tumba la app al arrancar, solo falla al pulsar el botón)."""
    global _chain
    if _chain is None:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        _chain = prompt | llm
    return _chain


# Caché simple en memoria: si los datos no cambian, no se vuelve a llamar a la API
_cache = {}


def elegir_tono(datos: dict) -> str:
    """Decide el tipo de mensaje (alerta o positivo) según los datos reales."""
    if datos["total"] == 0:
        return "motivador: el catálogo está vacío, invita a agregar la primera reseña"
    if datos["promedio"] is not None and datos["promedio"] < 3:
        return "de alerta amable: el promedio es bajo, sugiere buscar mejores opciones"
    if datos["sin_calificar"] > 0:
        return "positivo, e invita a calificar las reseñas que aún no tienen calificación"
    return "positivo y celebratorio"


def generar_mensaje(datos: dict) -> str:
    """Genera el texto con IA a partir del resumen del catálogo."""
    clave = str(sorted(datos.items()))
    if clave in _cache:
        return _cache[clave]

    entrada = {
        **datos,
        "promedio": datos["promedio"] if datos["promedio"] is not None else "sin datos",
        "tono": elegir_tono(datos),
    }
    texto = _get_chain().invoke(entrada).content
    _cache[clave] = texto
    return texto
