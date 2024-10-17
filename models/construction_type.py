from odoo import api, models, fields, _

class ConstructionType(models.Model):
    _name = 'construction.type'
    _description = "Type d'ouvrage"

    name = fields.Char(string="Type d'ouvrage", required=True)
    description = fields.Text(string="Description")
    etape_ids = fields.One2many('construction.etape', 'type_ouvrage_id', string="Étapes")
    cout_material = fields.Float(string="Coût du matériel")
    cout_construction = fields.Float(string="Coût construction")
    materiaux_ids = fields.One2many('construction.materiaux.type', 'type_id', string="Materiaux")
