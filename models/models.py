from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json

class ResCompany(models.Model):
    """
    Esta clase extiende el modelo `res.company` para añadir campos personalizados relacionados
    con la configuración de la API de Perú (API PERÚ). Proporciona los campos para almacenar
    el token de autenticación y el endpoint de la API.
    """
    _inherit = 'res.company'

    # Campo para definir el endpoint de la API de Perú.
    api_peru_endpoint = fields.Char(
        string="API Perú - Endpoint", 
        default='https://apiperu.dev',
        help="URL del servicio de API de Perú."
    )
    
    # Campo para definir el token de autenticación de la API de Perú.
    api_peru_token = fields.Char(
        string="API Perú - Token",
        help="Token de autenticación proporcionado por API Perú para hacer las solicitudes."
    )


class ResPartner(models.Model):
    """
    Extiende el modelo `res.partner` para permitir la autocompletación de datos de contactos
    utilizando la API PERÚ para consultas de RUC y DNI. La información se rellena automáticamente
    en los campos correspondientes al ingresar un número de identificación válido.
    """
    _inherit = 'res.partner'
    
    # Campo que referencia el tipo de identificación (DNI, RUC, etc.)
    identification_type = fields.Many2one(
        'l10n_latam.identification.type', 
        string="Tipo de Identificación",
        help="Selecciona el tipo de identificación como RUC o DNI."
    )
    
    # Campo que asocia el tipo de identificación con la localización de LATAM.
    l10n_latam_identification_type_id = fields.Many2one(
        'l10n_latam.identification.type', 
        string="Tipo de Identificación Latam",
        help="Campo para asignar automáticamente el tipo de identificación seleccionado."
    )

    @api.onchange('vat', 'identification_type')
    def _onchange_vat(self):
        """
        Método que se ejecuta automáticamente cuando cambian los valores de los campos
        `vat` o `identification_type`. Realiza la solicitud a la API PERÚ para obtener
        los datos del contacto basados en el número de RUC o DNI y los rellena
        automáticamente en los campos correspondientes.
        """
        if self.vat and self.identification_type:
            # Asigna el tipo de identificación seleccionado al campo Latam.
            self.l10n_latam_identification_type_id = self.identification_type

            # Obtiene la configuración de la compañía actual.
            company = self.env.company
            endpoint = company.api_peru_endpoint
            token = company.api_peru_token

            # Verifica que el endpoint y el token estén configurados.
            if not endpoint or not token:
                raise UserError(_("El token de la API o el endpoint no están configurados en la compañía."))

            # Define los encabezados de la solicitud HTTP.
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            # Prepara la URL y el payload según el tipo de identificación.
            url, payload = None, None
            if self.identification_type.name == 'DNI':
                url = f"{endpoint}/api/dni"
                payload = {"dni": self.vat}
            elif self.identification_type.name == 'RUC':
                url = f"{endpoint}/api/ruc"
                payload = {"ruc": self.vat}

            # Verifica que tanto la URL como el payload hayan sido correctamente configurados.
            if not url or not payload:
                raise UserError(_("El tipo de identificación no es válido o no está soportado."))

            try:
                # Realiza la solicitud POST a la API PERÚ con un timeout de 10 segundos.
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
                # Lanza una excepción si el código de estado HTTP indica un error.
                response.raise_for_status()
            except requests.exceptions.Timeout:
                # Error si la solicitud excede el tiempo de espera.
                raise UserError(_("La solicitud a la API tomó demasiado tiempo. Intenta nuevamente."))
            except requests.exceptions.RequestException as e:
                # Error genérico de conexión.
                raise UserError(_("Error de conexión con la API: %s") % str(e))

            # Intenta decodificar la respuesta de la API en formato JSON.
            try:
                result = response.json()
            except json.JSONDecodeError:
                # Error si la respuesta no puede ser decodificada como JSON.
                raise UserError(_("No se pudo decodificar la respuesta de la API. Verifica la respuesta recibida."))

            # Si la solicitud fue exitosa y `success` es True, procesa los datos.
            if result.get('success'):
                data = result.get('data', {})

                # Llenar los campos con los datos obtenidos del RUC o DNI.
                if self.identification_type.name == 'RUC':
                    self.name = data.get('nombre_o_razon_social', '')
                    self.is_company = True
                else:
                    self.name = data.get('nombre_completo')

                # Establece el país a Perú automáticamente.
                self.country_id = self.env.ref('base.pe').id

                # Maneja los valores para departamento, provincia, distrito, etc.
                department_name = data.get('departamento')
                if department_name:
                    department_name = f"{department_name.capitalize()} (PE)"
                    state = self.env['res.country.state'].search([('name', '=', department_name)], limit=1)
                    if state:
                        self.state_id = state.id

                city_name = data.get('provincia')
                if city_name:
                    self.city = city_name.capitalize()

                district_name = data.get('distrito')
                if district_name:
                    district_name = district_name.capitalize()
                    district = self.env['l10n_pe.res.city.district'].search([('name', '=', district_name)], limit=1)
                    if district:
                        self.l10n_pe_district = district.id

                # Completa la dirección y el código postal.
                self.street = data.get('direccion', '')
                self.zip = data.get('ubigeo_sunat', '')

            else:
                # Si la API no devuelve `success`, muestra un mensaje de error.
                raise UserError(_("La consulta a la API no fue exitosa. Verifica el número de %s.") % self.identification_type.name)
