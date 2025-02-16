# Copyright 2022 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    need_tax_round_down = fields.Boolean(
        default=False,
        help="If selected, rounding method 'DOWN' will be applied to tax amounts.",
    )
