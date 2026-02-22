
"""
hoja_firmas.py
--------------
A partir de un CSV con columnas 'Nombre' y 'Apellido(s)',
genera una hoja de firmas en PDF con los alumnos:
  - Ordenados alfabeticamente por apellido y luego nombre
  - En grupos de 8
  - Con columnas para Dia 1 (Lunes) y Dia 2 (Jueves)
  - Con tests unitarios incluidos

Uso:
    python hoja_firmas.py                        -> genera hoja_firmas.pdf
    python hoja_firmas.py --csv otro.csv         -> usa otro CSV
    python hoja_firmas.py --test                 -> ejecuta los tests
"""

import csv
import sys
import unittest
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Spacer, Paragraph, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


# =============================================================================
# LOGICA PRINCIPAL
# =============================================================================

def leer_csv(ruta):
    """
    Lee el CSV del profesor y devuelve una lista de tuplas (nombre, apellidos).
    El separador es '; ' (punto y coma con espacio).
    """
    alumnos = []
    with open(ruta, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # saltar cabecera
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

    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'titulo_doc',
        parent=estilos['Title'],
        fontSize=16,
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    estilo_grupo = ParagraphStyle(
        'titulo_grupo',
        parent=estilos['Heading2'],
        fontSize=11,
        spaceBefore=12,
        spaceAfter=4,
        textColor=colors.HexColor('#2c3e50'),
    )

    elementos = []

    # Titulo principal del documento
    elementos.append(Paragraph("Hoja de Firmas - Curso", estilo_titulo))
    elementos.append(Spacer(1, 0.3 * cm))

    ancho_pagina = A4[0] - 3 * cm  # ancho util
    col_widths = [
        ancho_pagina * 0.22,  # Nombre
        ancho_pagina * 0.28,  # Apellidos
        ancho_pagina * 0.25,  # Dia 1 (Lunes)
        ancho_pagina * 0.25,  # Dia 2 (Jueves)
    ]

    for i, grupo in enumerate(grupos):
        elementos.append(Paragraph(f"Grupo {i + 1}  ({len(grupo)} alumnos)", estilo_grupo))

        # Fila de cabecera de la tabla
        datos = [["Nombre", "Apellido(s)", "Día 1 (Lunes)", "Día 2 (Jueves)"]]

        for nombre, apellidos in grupo:
            datos.append([nombre, apellidos, "", ""])

        tabla = Table(datos, colWidths=col_widths, repeatRows=1)
        tabla.setStyle(TableStyle([
            # Cabecera
            ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0), 9),
            ('ALIGN',         (0, 0), (-1, 0), 'CENTER'),

            # Filas de datos
            ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',      (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),

            # Borde general
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),

            # Altura de fila generosa para poder firmar
            ('ROWHEIGHT',     (0, 1), (-1, -1), 22),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING',       (0, 0), (-1, -1), 5),
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 0.4 * cm))

        # Salto de pagina entre grupos (excepto el ultimo)
        if i < len(grupos) - 1:
            elementos.append(PageBreak())

    doc.build(elementos)
    print(f"✅ PDF generado correctamente: {ruta_salida}")
    print(f"   Total alumnos: {len(alumnos)}")
    print(f"   Total grupos:  {len(grupos)}")


# =============================================================================
# TESTS UNITARIOS
# =============================================================================

class TestHojaFirmas(unittest.TestCase):

    def test_ordenar_por_apellido(self):
        """Los alumnos deben ordenarse primero por apellido."""
        alumnos = [
            ('Carlos', 'Perez'),
            ('Ana',    'Garcia'),
            ('Luis',   'Garcia'),
        ]
        resultado = ordenar_alfabeticamente(alumnos)
        # Garcia debe ir antes que Perez
        self.assertEqual(resultado[0][1], 'Garcia')
        self.assertEqual(resultado[1][1], 'Garcia')
        self.assertEqual(resultado[2][1], 'Perez')

    def test_ordenar_mismo_apellido_por_nombre(self):
        """Con mismo apellido, se ordena por nombre."""
        alumnos = [
            ('Luis', 'Garcia'),
            ('Ana',  'Garcia'),
        ]
        resultado = ordenar_alfabeticamente(alumnos)
        self.assertEqual(resultado[0][0], 'Ana')
        self.assertEqual(resultado[1][0], 'Luis')

    def test_agrupar_exacto(self):
        """16 alumnos deben dar exactamente 2 grupos de 8."""
        alumnos = [(f'N{i}', f'A{i}') for i in range(16)]
        grupos = agrupar(alumnos, 8)
        self.assertEqual(len(grupos), 2)
        self.assertEqual(len(grupos[0]), 8)
        self.assertEqual(len(grupos[1]), 8)

    def test_agrupar_con_resto(self):
        """20 alumnos con grupos de 8 -> 2 grupos de 8 y 1 de 4."""
        alumnos = [(f'N{i}', f'A{i}') for i in range(20)]
        grupos = agrupar(alumnos, 8)
        self.assertEqual(len(grupos), 3)
        self.assertEqual(len(grupos[0]), 8)
        self.assertEqual(len(grupos[1]), 8)
        self.assertEqual(len(grupos[2]), 4)

    def test_leer_csv(self):
        """El CSV del profesor debe leerse correctamente."""
        import tempfile
        contenido = "Nombre; Apellido(s)\nPikachu; Aurelius\nCharizard; Julius\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                         delete=False, encoding='utf-8') as f:
            f.write(contenido)
            ruta_tmp = f.name
        try:
            alumnos = leer_csv(ruta_tmp)
            self.assertEqual(len(alumnos), 2)
            self.assertIn(('Pikachu', 'Aurelius'), alumnos)
            self.assertIn(('Charizard', 'Julius'), alumnos)
        finally:
            os.unlink(ruta_tmp)

    def test_generar_pdf_crea_archivo(self):
        """La funcion debe crear el archivo PDF en disco."""
        import tempfile
        alumnos = [(f'Nombre{i}', f'Apellido{i}') for i in range(10)]
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            ruta_tmp = f.name
        try:
            generar_pdf(alumnos, ruta_tmp)
            self.assertTrue(os.path.exists(ruta_tmp))
            self.assertGreater(os.path.getsize(ruta_tmp), 0)
        finally:
            os.unlink(ruta_tmp)


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == '__main__':
    if '--test' in sys.argv:
        # Ejecutar tests
        sys.argv.remove('--test')
        unittest.main(verbosity=2)
    else:
        # Determinar ruta del CSV
        ruta_csv = 'pokemons_participantes_curso.csv'
        if '--csv' in sys.argv:
            idx = sys.argv.index('--csv')
            ruta_csv = sys.argv[idx + 1]

        alumnos = leer_csv(ruta_csv)
        generar_pdf(alumnos)