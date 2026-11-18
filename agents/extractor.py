import os
import json
import fitz  # pymupdf
from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("API_KEY"))

PROMPT = """
Analizá esta factura y extraé los datos en formato JSON.
Devolvé SOLO el JSON, sin texto adicional, con esta estructura:

{
  "proveedor": "nombre del proveedor",
  "fecha": "dd/mm/aaaa",
  "nro_factura": "número de factura",
  "items": [
    {
      "articulo": "nombre del artículo",
      "cantidad": número,
      "unidad": "kg / unidad / litro / etc",
      "precio_total": número,
      "precio_unitario": número
    }
  ],
  "total": número
}

Si un campo no aparece en la factura, usá null.
El precio_unitario es precio_total / cantidad.
"""

def pdf_a_jpg(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(dpi=200)
    jpg_path = pdf_path.replace(".pdf", ".jpg")
    pix.save(jpg_path)
    return jpg_path

def extraer_factura(imagen_path: str) -> dict:
    if imagen_path.lower().endswith(".pdf"):
        imagen_path = pdf_a_jpg(imagen_path)

    with open(imagen_path, "rb") as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            PROMPT,
        ],
    )

    texto = response.text.strip()
    if texto.startswith("```"):
        texto = texto.split("```")[1]
        if texto.startswith("json"):
            texto = texto[4:]

    return json.loads(texto)
