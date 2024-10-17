from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Res Company'

    journal_id = fields.Many2one('account.journal', "Journal d'assurance")
    product_id = fields.Many2one('product.product', 'Article',
                                 help="Cet article sera utilisé pour les droits d'inscription")
