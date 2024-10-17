from odoo import models, fields, api, _

class ProjectProject(models.Model):
    _inherit = 'project.project'

    ouvrage_id = fields.Many2one('construction.ouvrage', string="Ouvrage")
    entrepreneur_id = fields.Many2one('res.partner', string="Entrepreneur associé", domain=[('is_company', '=', True)],
                                      required=True)