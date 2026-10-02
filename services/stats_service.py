def obtener_resumen(coleccion):
    """
    Dato clave: resumen del catálogo de reseñas.
    Devuelve un diccionario con cifras reales calculadas desde MongoDB.
    """
    resenas = list(coleccion.find())
    total = len(resenas)

    # 'calificacion' es opcional: solo existe en algunos documentos
    calificadas = [r for r in resenas if r.get("calificacion")]
    sin_calificar = total - len(calificadas)

    if calificadas:
        promedio = round(sum(r["calificacion"] for r in calificadas) / len(calificadas), 2)
        mejor = max(calificadas, key=lambda r: r["calificacion"])
        peor = min(calificadas, key=lambda r: r["calificacion"])
        mejor_txt = f'{mejor["titulo"]} ({mejor["calificacion"]}/5)'
        peor_txt = f'{peor["titulo"]} ({peor["calificacion"]}/5)'
    else:
        promedio = None
        mejor_txt = "n/a"
        peor_txt = "n/a"

    # Conteo por tipo: Película, Libro, Restaurante
    por_tipo = {}
    for r in resenas:
        tipo = r.get("tipo", "Sin tipo")
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

    return {
        "total": total,
        "sin_calificar": sin_calificar,
        "promedio": promedio,
        "por_tipo": ", ".join(f"{k}: {v}" for k, v in por_tipo.items()) or "ninguna",
        "mejor": mejor_txt,
        "peor": peor_txt,
    }
