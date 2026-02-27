"""
test_hoja_firmas.py
-------------------
Tests unitarios para hoja_firmas.py

Uso:
    python test_hoja_firmas.py
"""

import unittest
import tempfile
import os

from hoja_firmas import leer_csv, ordenar_alfabeticamente, agrupar, generar_pdf


class TestHojaFirmas(unittest.TestCase):

    def test_ordenar_por_apellido(self):
        """Los alumnos deben ordenarse primero por apellido."""
        alumnos = [
            ('Carlos', 'Perez'),
            ('Ana',    'Garcia'),
            ('Luis',   'Garcia'),
        ]
        resultado = ordenar_alfabeticamente(alumnos)
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
        """El CSV debe leerse correctamente."""
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
        alumnos = [(f'Nombre{i}', f'Apellido{i}') for i in range(10)]
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            ruta_tmp = f.name
        try:
            generar_pdf(alumnos, ruta_tmp)
            self.assertTrue(os.path.exists(ruta_tmp))
            self.assertGreater(os.path.getsize(ruta_tmp), 0)
        finally:
            os.unlink(ruta_tmp)


if __name__ == '__main__':
    unittest.main(verbosity=2)
