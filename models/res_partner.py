from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    est_entrepreneur = fields.Boolean("Est entrepreneur ?")
    ouvrage_ids = fields.One2many('construction.ouvrage', 'entrepreneur_id',  string="Ouvrages", ondelete='cascade')
    nbr_ouvrage_en_cours = fields.Integer(string="Ouvrages cours", compute='get_nombre_ouvrage', store=False)
    nbr_ouvrage_termine = fields.Integer(string="Ouvrages terminé", compute='get_nombre_ouvrage', store=False)
    nbr_ouvrage_confirme = fields.Integer(string="Ouvrages confirmé", compute='get_nombre_ouvrage', store=False)
    total_facture = fields.Integer(string="Total Factures validé", compute='get_nombre_ouvrage', store=False)
    total_du = fields.Integer(string="Total Factures dû", compute='get_nombre_ouvrage', store=False)
    nbr_facture = fields.Integer(string="Nombre Facture validée", compute='get_nombre_ouvrage', store=True)

    def get_nombre_ouvrage(self):
        for line in self:
            line.nbr_ouvrage_en_cours = self.env['construction.ouvrage'].search_count([('statut', '=', 'en_cours'), ('entrepreneur_id', '=', line.id)])
            line.nbr_ouvrage_termine = self.env['construction.ouvrage'].search_count([('statut', '=', 'termine'), ('entrepreneur_id', '=', line.id)])
            line.nbr_ouvrage_confirme = self.env['construction.ouvrage'].search_count([('statut', '=', 'confirme'), ('entrepreneur_id', '=', line.id)])
            line.nbr_facture = self.env['account.move'].search_count([('state', '=', 'posted'), ('partner_id', '=', line.id), ('amount_residual', '>', 0)])
            nbr_total_facture = self.env['account.move'].search([('state', '=', 'posted'), ('partner_id', '=', line.id), ('amount_residual', '>', 0)])
            line.total_du = sum(col.amount_residual for col in nbr_total_facture)
            total_facture = self.env['account.move'].search([('state', '=', 'posted'), ('partner_id', '=', line.id)])
            line.total_facture = sum(col.amount_total for col in total_facture)