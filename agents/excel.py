import os
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
load_dotenv()
SHEET_ID = os.getenv("SHEET_ID")

def get_sheet():
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1

def guardar_factura(datos: dict):
    sheet = get_sheet()
    for item in datos["items"]:
        fila = [
            datos.get("proveedor"),
            datos.get("fecha"),
            datos.get("nro_factura"),
            item.get("articulo"),
            item.get("cantidad"),
            item.get("unidad"),
            item.get("precio_unitario"),
            item.get("precio_total"),
            datos.get("total"),
        ]
        sheet.append_row(fila)
