# -*- coding: utf-8 -*-
{
    'name': "Consulta SUNAT con API PERÚ",
    'summary': "Autocompleta datos empresariales y personales en res.partner utilizando la API PERÚ para consultas de RUC y DNI.",
    'description': """
        El módulo "Consulta SUNAT con API PERÚ" proporciona una integración eficiente con la API PERÚ, permitiendo a los usuarios autocompletar información clave de contactos en Odoo utilizando solo el RUC o el DNI.

        **Características principales:**
        - Autocompletar información empresarial como razón social, domicilio fiscal, departamento, provincia y ubigeo al ingresar el número de RUC.
        - Autocompletar nombres y apellidos completos al ingresar el número de DNI.
        - Ahorra tiempo en la entrada manual de datos y mejora la precisión de la información.
        - Información actualizada directamente desde SUNAT.
        - Simplifica la gestión de contactos en Odoo para empresas que manejan grandes volúmenes de datos.
    """,
    'author': "Juan Salvador",
    'website': 'https://github.com/juansalvador/consulta_sunat',
    'category': 'Localization/Peru',
    'version': '1.0',
    'depends': [
        'base',
        'web',
        'l10n_latam_base',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
    ],
    'images': [
        'static/description/screen_1.png',
        'static/description/screen_2.png',
    ],
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
