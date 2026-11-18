import os
from google import genai
from agents.excel import get_sheet
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("API_KEY"))

COLUMNAS = ["proveedor", "fecha", "nro_factura", "articulo", "cantidad", "unidad", "precio_unitario", "precio_total", "total_factura"]

SYSTEM_PROMPT = """Sos un analista de compras con acceso al historial de facturas de proveedores.
Los datos están en CSV con columnas: proveedor, fecha (dd/mm/aaaa), nro_factura, articulo, cantidad, unidad, precio_unitario, precio_total, total_factura.
Cada fila es un ítem de una factura. Filas con mismo nro_factura pertenecen a la misma factura.
Respondé en español, claro y conciso. Si hacés cálculos, mostrá el resultado directo."""


def _cargar_historial() -> str:
    sheet = get_sheet()
    filas = sheet.get_all_values()
    if not filas:
        return "Sin datos."
    encabezado = ",".join(COLUMNAS)
    lineas = [encabezado]
    for fila in filas:
        fila_norm = (fila + [""] * len(COLUMNAS))[: len(COLUMNAS)]
        lineas.append(",".join(str(v) for v in fila_norm))
    return "\n".join(lineas)


def responder_pregunta(pregunta: str) -> str:
    historial = _cargar_historial()
    prompt = f"{SYSTEM_PROMPT}\n\nHistorial:\n{historial}\n\nPregunta: {pregunta}"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt],
    )
    return response.text.strip()
