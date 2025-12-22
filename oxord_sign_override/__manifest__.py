{
    "name": "OXORD Sign Override3",
    "version": "1.0",
    "summary": "Hide sign frame styling in Odoo 19",
    "author": "OXORD Computer Solutions & Repair Center",
    "category": "Customization",
    "depends": ["sign", "web"],
    "assets": {
        "web.assets_backend": [
            "oxord_sign_override/static/src/scss/sign_override.scss",
        ],
    },
    "installable": True,
    "application": False,
}
