from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ConstructionOuvrage(models.Model):
    _name = 'construction.ouvrage'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Héritage des fonctionnalités de messagerie

    _description = 'Construction Ouvrage'

    name = fields.Char(string="Libellé de l'ouvrage", required=True)
    type_ouvrage_id = fields.Many2one('construction.type', string="Type d'ouvrage", required=True)
    lot = fields.Char(string="Lot")
    ilot = fields.Char(string="Ilot")
    cout_ouvrage = fields.Float(string="Coût de l'ouvrage", compute='_compute_cout_ouvrage', store=True)
    entrepreneur_id = fields.Many2one('res.partner', string="Entrepreneur associé", domain=[('is_company', '=', True)],
                                      required=True)
    client_id = fields.Many2one('res.partner', string="Client", required=False)
    superviseur_id = fields.Many2one('res.users', string="Chef de projet", required=False)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    invoice_id = fields.Many2one('account.move', string='Facture')
    materiaux_ids = fields.One2many('construction.materiaux', 'ouvrage_id', string="Liste des matériaux")
    etapes_ids = fields.Many2many('construction.etape','rel_etape', 'ouvrage_id', 'etape_id', string="Liste des matériaux")
    date_debut = fields.Date(string="Date de début")
    date_fin = fields.Date(string="Date de fin")
    statut = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('confirme', 'Confirmé'),
        ('en_cours', 'En cours'),
        ('suspendu', 'Suspendu'),
        ('termine', 'Terminé')
    ], string="Statut", default='brouillon')
    type_contrat = fields.Selection([
        ('pause-fourniture', "Pause & Fourniture"),
        ('pause-simple', "Pause simple")
    ], string="Statut", default='pause-simple')
    pourcentage_realisation = fields.Float(string="Pourcentage de réalisation", compute='_compute_pourcentage',
                                           store=True)
    prix_vente = fields.Float(string="Prix de vente")
    benefice_realise = fields.Float(string="Bénéfice réalisé", compute='_compute_benefice', store=True)
    code_ouvrage = fields.Char(string="Code de l'ouvrage", required=True, copy=False, readonly=True,
                               default=lambda self: _('New'))
    numero = fields.Char(string="Numéro")
    longitude = fields.Float(string="Longitude")
    latitude = fields.Float(string="Latitude")
    project_id = fields.Many2one('project.project', string="Chantier associé", readonly=True)
    # Nouveaux champs
    jours_total_construction = fields.Integer(string="Nombre total (Jour)",
                                              compute='_compute_jours_total', store=True)
    jours_restants = fields.Integer(string="Nombre restant (Jour)", compute='_compute_jours_restants', store=True)
    # Nouveaux champs pour le coût
    cout_material = fields.Float(string="Coût du matériel")
    cout_construction = fields.Float(string="Coût construction")

    def open_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facture Fournisseur',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    def action_generer_facture_fournisseur(self):
        for rec in self:
            if not rec.invoice_id:
                journal = self.env.user.company_id.journal_id
                currency = self.env.user.company_id.currency_id
                product = self.env.user.company_id.product_id
                res = []
                if rec.cout_material == 0 and rec.cout_construction == 0:
                    raise ValidationError(
                        _("Veuillez renseigner le cout des matériaux et le cout de la construction."))
                if not journal:
                    raise ValidationError(
                        _("You must define the journal that will be used to post invoices"
                          "in company settings."))
                if not currency:
                    raise ValidationError(
                        _("You must define the currency that will be used to post the invoices"
                          "in company settings."))
                if not product:
                    raise ValidationError(
                        _("You must define the item that will be used for posting."))
                if rec.type_contrat == 'pause-fourniture' and rec.cout_material > 0:
                    product_vals = {
                        'product_id': product.id,
                        'quantity': 1,
                        'price_unit': rec.cout_material * 1,
                        'name': "Matériaux global",
                        'tax_ids': [(5, 0, 0)],
                    }
                    res.append(product_vals)

                if rec.cout_construction > 0:
                    product_vals = {
                        'product_id': product.id,
                        'quantity': 1,
                        'price_unit': rec.cout_construction * 1,
                        'name': "Contruction",
                        'tax_ids': [(5, 0, 0)],
                    }
                    res.append(product_vals)

                biling_rec = {
                    'move_type': 'in_invoice',
                    'journal_id': journal.id,
                    'ouvrage': True,
                    'partner_id': rec.entrepreneur_id.id,
                    'date': fields.Date.today(),
                    'invoice_date': fields.Date.today(),
                    'currency_id': currency.id,
                    'invoice_line_ids': [(0, 0, line) for line in res],
                    'state': 'draft',
                    'ref': rec.name
                }
                bill_created = self.env['account.move'].create(biling_rec)
                rec.invoice_id = bill_created



    @api.onchange('type_ouvrage_id')
    def _onchange_type_ouvrage(self):
        if self.type_ouvrage_id:
            # Récupérer les étapes associées au type d'ouvrage sélectionné
            etapes = self.env['construction.etape'].search([('type_ouvrage_id', '=', self.type_ouvrage_id.id)])
            self.etapes_ids = [(6, 0, etapes.ids)]  # Mettre à jour le champ etapes_ids avec les étapes trouvées
            self.cout_material = self.cout_material
            self.cout_construction = self.cout_construction
        else:
            self.etapes_ids = [(5, 0, 0)]  # Réinitialiser les étapes si aucun type d'ouvrage n'est sélectionné
            self.cout_material = 0
            self.cout_construction = 0

    @api.depends('date_debut', 'date_fin')
    def _compute_jours_total(self):
        for record in self:
            if record.date_debut and record.date_fin:
                # Calculer le nombre total de jours entre les dates de début et de fin
                start_date = fields.Date.from_string(record.date_debut)
                end_date = fields.Date.from_string(record.date_fin)
                record.jours_total_construction = (end_date - start_date).days
            else:
                record.jours_total_construction = 0

    @api.depends('date_fin')
    def _compute_jours_restants(self):
        for record in self:
            if record.date_fin:
                # Calculer le nombre de jours restants jusqu'à la date de fin
                end_date = fields.Date.from_string(record.date_fin)
                today = fields.Date.context_today(self)
                record.jours_restants = max((end_date - today).days, 0)  # Ne pas avoir de jours restants négatifs
            else:
                record.jours_restants = 0

    def action_confirmer(self):
        for record in self:
            if record.statut == 'brouillon':
                record.statut = 'confirme'
            else:
                raise UserError("L'ouvrage doit être en statut 'Brouillon' pour être confirmé.")

    def action_demarrer(self):
        for record in self:
            if record.statut == 'confirme':
                record.statut = 'en_cours'
            else:
                raise UserError("L'ouvrage doit être en statut 'Confirmé' pour être démarré.")

    def action_suspendre(self):
        for record in self:
            if record.statut == 'en_cours':
                record.statut = 'suspendu'
            else:
                raise UserError("L'ouvrage doit être en statut 'En cours' pour être suspendu.")

    def action_terminer(self):
        for record in self:
            if record.statut in ['en_cours', 'suspendu']:
                record.statut = 'termine'
            else:
                raise UserError("L'ouvrage doit être en statut 'En cours' ou 'Suspendu' pour être terminé.")

    def action_remettre_brouillon(self):
        for record in self:
            record.statut = 'brouillon'

    @api.model
    def create(self, vals):
        # Générer un code unique pour chaque ouvrage
        if vals.get('code_ouvrage', _('New')) == _('New'):
            vals['code_ouvrage'] = self.env['ir.sequence'].next_by_code('construction.ouvrage') or _('New')
        return super(ConstructionOuvrage, self).create(vals)

    @api.depends('prix_vente', 'cout_ouvrage')
    def _compute_benefice(self):
        for record in self:
            record.benefice_realise = record.prix_vente - record.cout_ouvrage

    @api.depends('cout_material', 'cout_construction')
    def _compute_cout_ouvrage(self):
        for record in self:
            record.cout_ouvrage = record.cout_material + record.cout_construction

    @api.depends('statut')
    def _compute_pourcentage(self):
        for record in self:
            if record.statut == 'termine':
                record.pourcentage_realisation = 100.0
            elif record.statut == 'en_cours':
                record.pourcentage_realisation = 50.0  # Exemple de calcul, à personnaliser
            else:
                record.pourcentage_realisation = 0.0

    def action_confirmer(self):
        for record in self:
            if record.statut == 'brouillon':
                record.statut = 'confirme'

                # Créer un projet dans le module Projet lié à cet ouvrage
                project_vals = {
                    'name': "%s - %s" % (record.name, record.client_id.name),
                    'partner_id': record.client_id.id,
                    'user_id': record.superviseur_id.id,
                    'date_start': record.date_debut,
                    'ouvrage_id': record.id,
                    'description': "Projet lié à l'ouvrage %s" % record.name,
                }
                project = self.env['project.project'].create(project_vals)
                record.project_id = project.id

                # Créer des tâches pour chaque étape associée
                for etape in record.etapes_ids:
                    task_vals = {
                        'name': etape.name,
                        'project_id': project.id,
                        'description': "Tâche liée à l'étape %s pour l'ouvrage %s" % (etape.name, record.name),
                    }
                    task = self.env['project.task'].create(task_vals)

                    # Créer des sous-tâches pour chaque sous-étape associée à l'étape
                    for sous_etape in etape.sous_etape_ids:  # Assurez-vous que `sous_etape_ids` existe dans le modèle Etape
                        subtask_vals = {
                            'name': sous_etape.name,
                            'project_id': project.id,
                            'parent_id': task.id,  # Lier la sous-tâche à la tâche principale
                            'description': "Sous-tâche liée à la sous-étape %s pour l'étape %s et l'ouvrage %s" % (
                                sous_etape.name, etape.name, record.name),
                        }
                        self.env['project.task'].create(subtask_vals)

            else:
                raise UserError("L'ouvrage doit être en statut 'Brouillon' pour être confirmé.")