from agents.extractor import extraer_factura
from agents.validador import comparar_precios
from agents.excel import guardar_factura
from agents.analista import responder_pregunta


def procesar_factura(imagen_path: str) -> dict:
    datos = extraer_factura(imagen_path)
    alertas = comparar_precios(datos)
    return {"datos": datos, "alertas": alertas}


def confirmar_guardado(datos: dict):
    guardar_factura(datos)


def consultar_historial(pregunta: str) -> str:
    return responder_pregunta(pregunta)
