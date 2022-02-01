{
    'name': 'Warranty',
    'depends': ['base',
                'stock',
                'account',
                'sale_management',
                ],

    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'view/warranty_property_views.xml',
        'view/warranty_menu.xml',

    ]
}