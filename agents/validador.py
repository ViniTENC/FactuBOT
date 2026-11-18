from agents.excel import get_sheet


def buscar_precio_anterior(articulo: str) -> float | None:
    sheet = get_sheet()
    celdas = sheet.findall(articulo)
    if not celdas:
        return None
    ultima = celdas[-1]
    fila = sheet.row_values(ultima.row)
    try:
        return float(fila[6])  # columna precio_unitario
    except (IndexError, ValueError):
        return None


def comparar_precios(datos: dict) -> list[dict]:
    alertas = []
    for item in datos["items"]:
        precio_anterior = buscar_precio_anterior(item["articulo"])
        if precio_anterior is None:
            continue
        precio_nuevo = item.get("precio_unitario", 0)
        if precio_anterior > 0:
            variacion = ((precio_nuevo - precio_anterior) / precio_anterior) * 100
            alertas.append({
                "articulo": item["articulo"],
                "precio_anterior": precio_anterior,
                "precio_nuevo": precio_nuevo,
                "variacion": round(variacion, 1),
            })
    return alertas
