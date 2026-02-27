"""
hoja_firmas.py
--------------
A partir de un CSV con columnas 'Nombre' y 'Apellido(s)',
genera una hoja de firmas en PDF con los alumnos:
  - Ordenados alfabeticamente por apellido y luego nombre
  - En grupos de 8
  - Con columnas para Dia 1 (Lunes) y Dia 2 (Jueves)

Uso:
    python hoja_firmas.py                 -> genera hoja_firmas.pdf
    python hoja_firmas.py --csv otro.csv  -> usa otro CSV
"""

import csv
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Spacer, Paragraph
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def leer_csv(ruta):
    """
    Lee el CSV y devuelve una lista de tuplas (nombre, apellidos).
    El separador es ';'.
    """
    alumnos = []
    with open(ruta, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for fila in reader:
            if len(fila) >= 2:
                nombre = fila[0].strip()
                apellidos = fila[1].strip()
                alumnos.append((nombre, apellidos))
    return alumnos


def ordenar_alfabeticamente(alumnos):
    """
    Ordena la lista de alumnos por apellidos y luego por nombre (A-Z).
    """
    return sorted(alumnos, key=lambda a: (a[1].lower(), a[0].lower()))


def agrupar(alumnos, tamano=8):
    """
    Divide la lista de alumnos en grupos de 'tamano' personas.
    El ultimo grupo puede tener menos si no es multiplo exacto.
    """
    return [alumnos[i:i + tamano] for i in range(0, len(alumnos), tamano)]


def generar_pdf(alumnos, ruta_salida='hoja_firmas.pdf'):
    """
    Genera el PDF de hoja de firmas a partir de la lista de alumnos.
    """
    alumnos_ordenados = ordenar_alfabeticamente(alumnos)
    grupos = agrupar(alumnos_ordenados)

    COL_NOMBRE   = 30
    COL_APELLIDO = 34
    COL_DIA      = 24
    col_w = [COL_NOMBRE, COL_APELLIDO, COL_DIA, COL_DIA]
    ancho_bloque = sum(col_w)

    ancho_util = A4[0] - 1.2 * cm
    gap = (ancho_util - 3 * ancho_bloque) / 2

    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=A4,
        rightMargin=0.6 * cm,
        leftMargin=0.6 * cm,
        topMargin=0.6 * cm,
        bottomMargin=0.6 * cm,
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'titulo_doc',
        parent=estilos['Title'],
        fontSize=9,
        spaceAfter=2,
        alignment=TA_CENTER,
    )
    estilo_grupo = ParagraphStyle(
        'titulo_grupo',
        parent=estilos['Normal'],
        fontSize=5.5,
        spaceBefore=0,
        spaceAfter=1,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold',
    )

    AZUL = '#2c3e50'
    GRIS = '#ecf0f1'

    def hacer_tabla(grupo):
        datos = [["Nombre", "Apellido(s)", "Dia 1\n(Lunes)", "Dia 2\n(Jueves)"]]
        for nombre, apellidos in grupo:
            datos.append([nombre, apellidos, "", ""])
        t = Table(datos, colWidths=col_w)
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor(AZUL)),
            ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0), 5),
            ('ALIGN',         (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',      (0, 1), (-1, -1), 5),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, colors.HexColor(GRIS)]),
            ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#bdc3c7')),
            ('ROWHEIGHT',     (0, 0), (0, 0), 14),
            ('ROWHEIGHT',     (0, 1), (-1, -1), 11),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING',   (0, 0), (-1, -1), 2),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 2),
            ('TOPPADDING',    (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        return t

    filas_grupos = [grupos[i:i + 3] for i in range(0, len(grupos), 3)]
    elementos = []
    elementos.append(Paragraph("Hoja de Firmas - Curso", estilo_titulo))
    elementos.append(Spacer(1, 0.2 * cm))

    for fila in filas_grupos:
        celdas = []
        col_widths_fila = []

        for idx_fila, grupo in enumerate(fila):
            idx = grupos.index(grupo)
            titulo = Paragraph(f"Grupo {idx + 1} ({len(grupo)} alumnos)", estilo_grupo)
            tabla = hacer_tabla(grupo)
            bloque = Table([[titulo], [tabla]], colWidths=[ancho_bloque])
            bloque.setStyle(TableStyle([
                ('LEFTPADDING',  (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING',   (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
            ]))
            celdas.append(bloque)
            col_widths_fila.append(ancho_bloque)

            if idx_fila < len(fila) - 1:
                celdas.append("")
                col_widths_fila.append(gap)

        while len(fila) < 3:
            celdas.append("")
            col_widths_fila.append(ancho_bloque)
            if len(fila) < 2:
                celdas.append("")
                col_widths_fila.append(gap)
            fila.append(None)

        fila_tabla = Table([celdas], colWidths=col_widths_fila)
        fila_tabla.setStyle(TableStyle([
            ('LEFTPADDING',  (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING',   (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
            ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ]))
        elementos.append(fila_tabla)

    doc.build(elementos)
    print(f"PDF generado: {ruta_salida}")
    print(f"Total alumnos: {len(alumnos)}")
    print(f"Total grupos:  {len(grupos)}")


if __name__ == '__main__':
    ruta_csv = 'pokemons_participantes_curso.csv'
    if '--csv' in sys.argv:
        idx = sys.argv.index('--csv')
        ruta_csv = sys.argv[idx + 1]

    alumnos = leer_csv(ruta_csv)
    generar_pdf(alumnos)
