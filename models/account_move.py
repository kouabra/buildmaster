from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'account.move'

    ouvrage = fields.Boolean("Ouvrage ?", default=False)