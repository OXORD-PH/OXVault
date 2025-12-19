{
    'name': 'OXORD Sign Override2',
    'version': '1.0',
    'author': 'OXORD Computer Solutions',
    'category': 'Tools',
    'summary': 'Override Sign module CSS to hide frame/footer',
    'depends': ['sign'],
    'assets': {
        'web.assets_frontend': [
            'oxord_sign_override/static/src/scss/sign_override.scss',
        ],
    },
    'installable': True,
    'application': False
}
