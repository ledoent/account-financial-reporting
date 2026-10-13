# © 2011 Guewen Baconnier (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).-
from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    centralized = fields.Boolean(
        help="If flagged, no details will be displayed in "
        "the General Ledger report (the webkit one only), "
        "only centralized amounts per period.",
    )

    # 20.0 dropped the account.group model; the chart hierarchy now lives on the
    # account itself as parent_id/parent_path. Core already supplies what the old
    # account.group extension computed by hand — code_path replaces complete_code
    # and name_path replaces complete_name — so the only thing left to add is the
    # set of accounts whose balances roll up into a node, which the trial balance
    # needs to total a hierarchy row.
    compute_account_ids = fields.Many2many(
        comodel_name="account.account",
        compute="_compute_compute_account_ids",
        string="Compute accounts",
        store=False,
    )

    @api.depends("parent_path")
    def _compute_compute_account_ids(self):
        # child_of walks the whole subtree via parent_path, so this covers every
        # level rather than only direct children, and it includes the node itself
        # because a parent account is postable in 20.0 and its own entries belong
        # in its total.
        for account in self:
            account.compute_account_ids = self.search([("id", "child_of", account.id)])
