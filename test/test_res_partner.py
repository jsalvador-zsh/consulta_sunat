# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from unittest.mock import patch
import requests

class TestResPartner(TransactionCase):
    """
    Pruebas unitarias para la funcionalidad de consultas RUC/DNI a través de la API PERÚ.
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas. Se ejecuta antes de cada prueba.
        """
        super(TestResPartner, self).setUp()
        
        # Crear una compañía de prueba y asignar un token ficticio y endpoint
        self.company = self.env['res.company'].create({
            'name': 'Test Company',
            'api_peru_token': 'test_token',
            'api_peru_endpoint': 'https://apiperu.dev'
        })
        
        # Crear un partner de prueba con un RUC ficticio
        self.partner_ruc = self.env['res.partner'].create({
            'name': 'Test Partner RUC',
            'vat': '20100443688',  # RUC de prueba
            'identification_type': self.env.ref('l10n_latam_base.it_ruc')
        })

        # Crear un partner de prueba con un DNI ficticio
        self.partner_dni = self.env['res.partner'].create({
            'name': 'Test Partner DNI',
            'vat': '12345678',  # DNI de prueba
            'identification_type': self.env.ref('l10n_latam_base.it_dni')
        })

    @patch('requests.post')
    def test_ruc_query_success(self, mock_post):
        """
        Prueba que la consulta RUC a la API devuelva una respuesta exitosa
        y que los datos sean rellenados correctamente en res.partner.
        """
        # Simula una respuesta de éxito de la API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "success": True,
            "data": {
                "nombre_o_razon_social": "EMPRESA DEMO",
                "direccion": "JR. ANDAHUAYLAS NRO. 100",
                "departamento": "Lima",
                "provincia": "Lima",
                "distrito": "Magdalena del Mar",
                "ubigeo_sunat": "150101"
            }
        }

        # Ejecuta el cambio de vat para realizar la consulta simulada
        self.partner_ruc._onchange_vat()

        # Verifica que los datos se hayan rellenado correctamente
        self.assertEqual(self.partner_ruc.name, "EMPRESA DEMO")
        self.assertEqual(self.partner_ruc.street, "JR. ANDAHUAYLAS NRO. 100")
        self.assertEqual(self.partner_ruc.city, "Lima")
        self.assertEqual(self.partner_ruc.zip, "150101")
    
    @patch('requests.post')
    def test_dni_query_success(self, mock_post):
        """
        Prueba que la consulta DNI a la API devuelva una respuesta exitosa
        y que los datos sean rellenados correctamente en res.partner.
        """
        # Simula una respuesta de éxito de la API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "success": True,
            "data": {
                "nombre_completo": "JUAN PEREZ"
            }
        }

        # Ejecuta el cambio de vat para realizar la consulta simulada
        self.partner_dni._onchange_vat()

        # Verifica que los datos se hayan rellenado correctamente
        self.assertEqual(self.partner_dni.name, "JUAN PEREZ")
    
    @patch('requests.post')
    def test_query_failure(self, mock_post):
        """
        Prueba que se maneje correctamente un fallo en la consulta a la API,
        mostrando un error adecuado si la API no devuelve éxito.
        """
        # Simula una respuesta fallida de la API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "success": False
        }

        # Intenta realizar la consulta con RUC y captura el error
        with self.assertRaises(UserError):
            self.partner_ruc._onchange_vat()

        # Intenta realizar la consulta con DNI y captura el error
        with self.assertRaises(UserError):
            self.partner_dni._onchange_vat()

    @patch('requests.post')
    def test_invalid_json_response(self, mock_post):
        """
        Prueba que se maneje correctamente una respuesta no válida (JSON corrupto).
        """
        # Simula una respuesta que no es JSON válido
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)

        # Intenta realizar la consulta y captura el error
        with self.assertRaises(UserError):
            self.partner_ruc._onchange_vat()
