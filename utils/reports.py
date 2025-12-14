import csv
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import os


def generar_excel(transacciones, filename="reporte_financiero.xlsx"):
    """Genera un archivo Excel con el historial de transacciones"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Historial"

    # Encabezados
    headers = ["ID", "Tipo", "Monto", "Categoría", "Fecha", "Descripción"]
    ws.append(headers)

    # Datos
    for t in transacciones:
        ws.append([t.id, t.tipo, t.monto, t.categoria, t.fecha, t.descripcion])

    # Guardar
    try:
        wb.save(filename)
        return f"Reporte Excel guardado como: {filename}"
    except Exception as e:
        return f"Error al guardar Excel: {e}"


def generar_pdf(transacciones, filename="reporte_financiero.pdf"):
    """Genera un reporte PDF básico con reportlab"""
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        # Título
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Reporte Financiero Personal")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # Encabezados de tabla manual (posición Y, posición X)
        y = height - 100
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Fecha")
        c.drawString(150, y, "Categoría")
        c.drawString(300, y, "Descripción")
        c.drawString(500, y, "Monto")

        c.line(50, y - 5, 550, y - 5)
        y -= 25

        # Filas
        c.setFont("Helvetica", 10)
        for t in transacciones:
            if y < 50:  # Nueva página si se acaba el espacio
                c.showPage()
                y = height - 50

            c.drawString(50, y, str(t.fecha))
            c.drawString(150, y, str(t.categoria))
            # Recortar descripción si es muy larga para el PDF
            desc = (t.descripcion[:30] + '..') if len(t.descripcion) > 30 else t.descripcion
            c.drawString(300, y, desc)

            # Color rojo para gastos, verde para ingresos
            if t.tipo == 'gasto':
                c.setFillColorRGB(0.8, 0, 0)
            else:
                c.setFillColorRGB(0, 0.5, 0)

            c.drawString(500, y, f"${t.monto:,.2f}")
            c.setFillColorRGB(0, 0, 0)  # Volver a negro
            y -= 20

        c.save()
        return f"Reporte PDF guardado como: {filename}"
    except Exception as e:
        return f"Error al generar PDF: {e}"