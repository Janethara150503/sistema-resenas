from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializar la aplicación Flask
app = Flask(__name__)

# Conexión a MongoDB Atlas usando la URI definida en las variables de entorno
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)

# Seleccionar la base de datos y la colección que vamos a usar
db = client["catalogo_resenas"]
resenas_collection = db["resenas"]


@app.route("/")
def index():
    """
    Ruta principal: lista todas las reseñas guardadas,
    ordenadas de la más reciente a la más antigua.
    """
    # sort("fecha", -1) ordena de forma descendente (más reciente primero)
    resenas = list(resenas_collection.find().sort("fecha", -1))
    return render_template("index.html", resenas=resenas)


@app.route("/agregar", methods=["POST"])
def agregar():
    """
    Ruta para agregar una nueva reseña.
    Los campos 'calificacion' e 'imagen_url' son opcionales:
    solo se incluyen en el documento si el usuario los llenó.
    """
    titulo = request.form.get("titulo", "").strip()
    tipo = request.form.get("tipo", "").strip()
    comentario = request.form.get("comentario", "").strip()
    calificacion = request.form.get("calificacion", "").strip()
    imagen_url = request.form.get("imagen_url", "").strip()

    # Construimos el documento base con los campos obligatorios
    nueva_resena = {
        "titulo": titulo,
        "tipo": tipo,
        "comentario": comentario,
        "fecha": datetime.utcnow()
    }

    # Solo agregamos 'calificacion' si el usuario la llenó,
    # y la convertimos a entero (nunca se guarda vacía o como null)
    if calificacion:
        nueva_resena["calificacion"] = int(calificacion)

    # Solo agregamos 'imagen_url' si el usuario proporcionó un enlace
    if imagen_url:
        nueva_resena["imagen_url"] = imagen_url

    # Insertar el documento en la colección
    resenas_collection.insert_one(nueva_resena)

    return redirect(url_for("index"))


@app.route("/eliminar/<id>", methods=["POST"])
def eliminar(id):
    """
    Ruta para eliminar una reseña según su _id.
    Convertimos el string recibido en un ObjectId de bson
    para poder hacer la búsqueda correctamente en MongoDB.
    """
    resenas_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("index"))


# Punto de entrada de la aplicación
if __name__ == "__main__":
    app.run(debug=True)