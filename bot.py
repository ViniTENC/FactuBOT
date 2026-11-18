import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, ConversationHandler
import pillow_heif
from PIL import Image
from orchestrator import procesar_factura, confirmar_guardado, consultar_historial

load_dotenv()

ESPERANDO_CONFIRMACION = 1

def convertir_a_jpg(path: str) -> str:
    if path.lower().endswith(".heic"):
        heif_file = pillow_heif.read_heif(path)
        image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data)
        jpg_path = path.replace(".heic", ".jpg").replace(".HEIC", ".jpg")
        image.save(jpg_path, "JPEG")
        os.remove(path)
        return jpg_path
    return path

async def recibir_archivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        path = "factura.jpg"
    else:
        file = await update.message.document.get_file()
        path = update.message.document.file_name

    await file.download_to_drive(path)
    path = convertir_a_jpg(path)
    await update.message.reply_text("Procesando factura...")

    resultado = procesar_factura(path)
    datos = resultado["datos"]
    alertas = resultado["alertas"]
    context.user_data["datos"] = datos

    resumen = f"*Proveedor:* {datos['proveedor']}\n"
    resumen += f"*Fecha:* {datos['fecha']}\n"
    resumen += f"*Factura N°:* {datos['nro_factura']}\n\n"
    resumen += "*Items:*\n"
    for item in datos["items"]:
        resumen += f"  - {item['articulo']}: {item['cantidad']} {item['unidad']} | unitario: ${item['precio_unitario']} | total: ${item['precio_total']}\n"
    resumen += f"\n*Total:* ${datos['total']}"
    await update.message.reply_text(resumen, parse_mode="Markdown")

    if alertas:
        msg = "*Comparación con facturas anteriores:*\n"
        for a in alertas:
            emoji = "🔴" if a["variacion"] > 5 else "🟡" if a["variacion"] > 0 else "🟢"
            msg += f"{emoji} {a['articulo']}: ${a['precio_anterior']} → ${a['precio_nuevo']} ({a['variacion']:+.1f}%)\n"
        await update.message.reply_text(msg, parse_mode="Markdown")

    teclado = ReplyKeyboardMarkup([["✅ Confirmar", "❌ Cancelar"]], one_time_keyboard=True)
    await update.message.reply_text("¿Guardamos la factura?", reply_markup=teclado)
    return ESPERANDO_CONFIRMACION

async def consulta_analista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pregunta = update.message.text
    await update.message.reply_text("Consultando historial...")
    respuesta = consultar_historial(pregunta)
    await update.message.reply_text(respuesta)

async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    respuesta = update.message.text
    if respuesta == "✅ Confirmar":
        datos = context.user_data.get("datos")
        confirmar_guardado(datos)
        await update.message.reply_text("Factura guardada en el Sheet.", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("Cancelado. No se guardó nada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.PHOTO | filters.Document.ALL, recibir_archivo)],
    states={
        ESPERANDO_CONFIRMACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar)],
    },
    fallbacks=[],
)

app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(conv_handler)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, consulta_analista))
app.run_polling()
