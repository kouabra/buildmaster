from odoo import models, fields, api

class Etape(models.Model):
    _name = 'construction.etape'
    _description = 'Étape'

    sequence = fields.Integer("Séquence", default=1)
    name = fields.Char("Nom de l'Étape", required=True)
    type_ouvrage_id = fields.Many2one('construction.type', string="Type d'Ouvrage", ondelete='cascade')
    sous_etape_ids = fields.Many2many('construction.sous.etape', 'etape_sous_etape_rel', 'etape_id', 'sous_etape_id',
                                      string="Sous-Étapes")


class SousEtape(models.Model):
    _name = 'construction.sous.etape'
    _description = 'Sous-Étape'

    sequence = fields.Integer("Séquence", default=1)
    name = fields.Char('Nom de la Sous-Étape', required=True)

