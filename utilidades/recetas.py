"""Generaci?n de recetas en PDF."""

from datetime import datetime
from pathlib import Path


def generar_pdf_receta(
    nombre_paciente,
    nombre_doctor,
    medicamento,
    dias_tratamiento,
    horario_suministro,
    indicaciones="",
    ruta_salida="receta.pdf"
):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
    except ImportError as exc:
        raise ImportError(
            "Para generar el archivo PDF instala 'reportlab' ejecutando:\n"
            "pip install reportlab"
        ) from exc

    c = canvas.Canvas(str(ruta_salida), pagesize=letter)
    ancho, alto = letter

    # Encabezado institucional
    c.setFillColor(colors.HexColor("#1F4E79"))
    c.rect(40, alto - 125, ancho - 80, 85, fill=1, stroke=0)

    ruta_logo = Path(__file__).resolve().parents[1] / "imagenes" / "nd.png"
    texto_x = 60
    if ruta_logo.exists():
        c.drawImage(
            str(ruta_logo),
            52,
            alto - 117,
            width=68,
            height=68,
            preserveAspectRatio=True,
            mask="auto"
        )
        texto_x = 135

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(texto_x, alto - 75, "NÚCLEO DE DIAGNÓSTICO")
    c.setFont("Helvetica", 11)
    c.drawString(texto_x, alto - 96, "Receta Médica")

    c.setFont("Helvetica", 9)
    fecha_emision = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    c.drawRightString(ancho - 55, alto - 112, f"Fecha: {fecha_emision}")

    # Datos del Paciente
    y = alto - 165
    c.setFillColor(colors.HexColor("#1F4E79"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "DATOS DEL PACIENTE")
    c.line(50, y - 5, ancho - 50, y - 5)

    y -= 28
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Paciente:")
    c.setFont("Helvetica", 11)
    c.drawString(120, y, nombre_paciente)

    # Información del Medicamento
    y -= 45
    c.setFillColor(colors.HexColor("#1F4E79"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "PRESCRIPCIÓN Y MEDICAMENTO INDICADO")
    c.line(50, y - 5, ancho - 50, y - 5)

    y -= 30
    c.setFillColor(colors.HexColor("#F4F7FA"))
    c.rect(50, y - 75, ancho - 100, 90, fill=1, stroke=1)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(65, y - 5, "Medicamento:")
    c.setFont("Helvetica", 11)
    c.drawString(165, y - 5, medicamento)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(65, y - 30, "Días de tratamiento:")
    c.setFont("Helvetica", 11)
    c.drawString(200, y - 30, dias_tratamiento)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(65, y - 55, "Horario de suministro:")
    c.setFont("Helvetica", 11)
    c.drawString(215, y - 55, horario_suministro)

    # Indicaciones / Diagnóstico
    if indicaciones.strip():
        y -= 115
        c.setFillColor(colors.HexColor("#1F4E79"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "INDICACIONES / DIAGNÓSTICO")
        c.line(50, y - 5, ancho - 50, y - 5)

        y -= 25
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        for linea in indicaciones.strip().splitlines()[:14]:
            c.drawString(55, y, linea[:95])
            y -= 15

    # Firma del Doctor
    firma_y = 110
    c.setStrokeColor(colors.HexColor("#1F4E79"))
    c.line(ancho / 2 - 130, firma_y, ancho / 2 + 130, firma_y)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(ancho / 2, firma_y - 18, f"Dr(a). {nombre_doctor}")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(ancho / 2, firma_y - 33, "Médico Tratante - Núcleo de Diagnóstico")

    c.save()
    return str(Path(ruta_salida).resolve())
