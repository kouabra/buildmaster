from odoo import models, fields


class ConstructionMateriaux(models.Model):
    _name = 'construction.materiaux'
    _description = "Matériaux utilisés pour l'ouvrage"

    product_id = fields.Many2one('product.product', string="Matériau", required=True)
    quantite = fields.Float(string="Quantité prévue", required=True)
    ouvrage_id = fields.Many2one('construction.ouvrage', string="Ouvrage", required=True)
    unite = fields.Many2one('uom.uom', string="Unité", required=True)  # Champ pour l'unité


class ConstructionMateriauxType(models.Model):
    _name = 'construction.materiaux.type'
    _description = "Matériaux utilisés pour l'ouvrage"

    product_id = fields.Many2one('product.product', string="Matériau", required=True)
    quantite = fields.Float(string="Quantité prévue", required=True)
    type_id = fields.Many2one('construction.type', string="Type", required=True)
    unite = fields.Many2one('uom.uom', string="Unité", required=True)  # Champ pour l'unité

