{
    'name': "Build Master",
    'version': '17.0.1.0.0',  # Version mise à jour pour Odoo 17
    'sequence': 3,
    'summary': "Realestate",
    'description': """
        Realestate
    """,
    'author': "",
    'category': "realestate",
    'license': 'LGPL-3',
    'website': '',  # Ajoutez un lien de site web si nécessaire

    'depends': [
        'base',
        'contacts',
        'account',
        'project',
        'stock',
        'sale',
        'purchase',
        'hr',
        'project',
        'mail',
        'utm',
    ],
    'data': [
        'data/sequence.xml',
        'data/contruction_etape_data.xml',
        'data/contruction_type_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/construction_ouvrage_view.xml',
        'views/contruction_type_view.xml',
        'views/project_project_view.xml',
        'views/res_partner_view.xml',
        'views/coustruction_etape_view.xml',
        'views/construction_sous_etape_view.xml',
        'views/demande_materiaux_view.xml',
        'views/res_company_views.xml',
        'views/analyse_view.xml',
        'views/menui_view.xml',
    ],
    'qweb': [],

    'installable': True,
    'application': True,
    'auto_install': False,
}
