from odoo import models, fields, api, _

from odoo.exceptions import UserError


class DemandeMateriaux(models.Model):
    _name = 'construction.demande.materiaux'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Héritage des fonctionnalités de messagerie
    _description = 'Demande de Matériaux'

    name = fields.Char(string="Objet de la demande", required=True)
    date = fields.Datetime(string="Date de la demande", required=True)
    chantier_id = fields.Many2one('construction.ouvrage', string="Chantier associé", required=True)
    etape_id = fields.Many2one('construction.etape', string="Étape associée", required=True)
    statut = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('en_attente_validation', 'En attente de validation'),
        ('valide', "Validé"),
        ('livre', "Livré"),
        ('cancel', "Anulmé")
    ], string="Statut", default='brouillon')
    detail_ids = fields.One2many('construction.demande.detail', 'demande_id', string="Détails de la demande")

    @api.model
    def create(self, vals):
        # Créer une nouvelle demande de matériaux
        return super(DemandeMateriaux, self).create(vals)

    def action_valider(self):
        # Passer à l'état "En attente de validation"
        for record in self:
            if record.statut == 'brouillon':
                record.statut = 'en_attente_validation'

    def action_livrer(self):
        # Passer à l'état "Terminé"
        for record in self:
            if record.statut == 'en_attente_validation':
                record.statut = 'livre'

    def action_generer_bon_livraison(self):
        for demande in self:
            if demande.statut != 'livre':
                raise UserError("La demande doit être dans un statut 'Terminé' pour générer un bon de livraison.")

            # Créer un bon de livraison
            picking_vals = {
                'partner_id': demande.chantier_id.entrepreneur_id.id,  # Assurez-vous d'avoir un partenaire lié au chantier
                'picking_type_id': self.env.ref('stock.picking_type_out').id,
                # Assurez-vous d'avoir un type de livraison défini
                'move_line_ids_without_package': [],
            }

            # Créer les lignes de mouvement pour chaque article demandé
            for detail in demande.detail_ids:
                move_vals = {
                    'name': detail.article_id.name,
                    'product_id': detail.article_id.id,
                    'product_uom_qty': detail.quantite,
                    'product_uom': detail.unite.id,  # Assurez-vous que le champ unité est rempli
                    #'picking_id': (4, picking.id),  # Associe les lignes au bon de livraison
                }
                #picking_vals['move_line_ids_without_package'].append((0, 0, move_vals))

            # Créer le bon de livraison
            picking = self.env['stock.picking'].create(picking_vals)

            # Enregistrer le bon de livraison
            picking.action_confirm()  # Confirme le bon de livraison
            picking.action_assign()  # Assigne les mouvements

            # Optionnel : Mettre à jour le statut de la demande
            demande.statut = 'livre'  # Ou selon votre logique de workflow

class DemandeMateriauxDetail(models.Model):
    _name = 'construction.demande.detail'
    _description = 'Détails de la Demande de Matériaux'

    demande_id = fields.Many2one('construction.demande.materiaux', string="Demande de Matériaux", required=True)
    article_id = fields.Many2one('product.product', string="Article", required=True)
    quantite = fields.Float(string="Quantité", required=True)
    unite = fields.Many2one('uom.uom', string="Unité", required=True)  # Champ pour l'unité

