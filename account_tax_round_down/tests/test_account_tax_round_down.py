# Copyright 2022-2024 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestAccountTaxRoundDown(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create(
            {
                "name": "test company",
                "currency_id": cls.env.ref("base.JPY").id,
                "country_id": cls.env.ref("base.jp").id,
                "tax_calculation_rounding_method": "round_per_line",
                "need_tax_round_down": False,
            }
        )
        cls.env.company = cls.company
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "tax 10",
                "type_tax_use": "sale",
                "amount": 10,
                "country_id": cls.env.ref("base.jp").id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {"code": "test", "name": "test", "type": "sale"}
        )
        cls.account_income = cls.env["account.account"].create(
            {
                "code": "test1",
                "name": "income",
                "account_type": "income",
            }
        )
        account_receivable = cls.env["account.account"].create(
            {
                "code": "test2",
                "name": "receivable",
                "reconcile": True,
                "account_type": "asset_receivable",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "test partner",
                "property_account_receivable_id": account_receivable.id,
            }
        )

    def _prepare_invoice_line_vals(self, price_unit=15):
        return {
            "name": "test",
            "account_id": self.account_income.id,
            "quantity": 1,
            "price_unit": price_unit,
            "tax_ids": [Command.set(self.tax.ids)],
        }

    def _create_invoice(self):
        return (
            self.env["account.move"]
            .with_company(self.company)
            .create(
                {
                    "move_type": "out_invoice",
                    "invoice_date": fields.Date.today(),
                    "partner_id": self.partner.id,
                    "currency_id": self.env.ref("base.JPY").id,
                    "invoice_line_ids": [
                        Command.create(self._prepare_invoice_line_vals())
                    ],
                }
            )
        )

    def test_round_per_line_round_down_false(self):
        company = self.company
        self.assertEqual(company.tax_calculation_rounding_method, "round_per_line")
        self.assertEqual(company.need_tax_round_down, False)
        invoice = self._create_invoice()
        self.assertEqual(invoice.amount_tax, 2)
        self.assertEqual(invoice.amount_total, 17)
        invoice.write(
            {
                "invoice_line_ids": [Command.create(self._prepare_invoice_line_vals())],
            }
        )
        self.assertEqual(invoice.amount_tax, 4)
        self.assertEqual(invoice.amount_total, 34)

    def test_round_per_line_round_down_true(self):
        company = self.company
        self.assertEqual(company.tax_calculation_rounding_method, "round_per_line")
        company.need_tax_round_down = True
        invoice = self._create_invoice()
        self.assertEqual(invoice.amount_tax, 1)
        self.assertEqual(invoice.amount_total, 16)
        invoice.write(
            {
                "invoice_line_ids": [Command.create(self._prepare_invoice_line_vals())],
            }
        )
        self.assertEqual(invoice.amount_tax, 2)
        self.assertEqual(invoice.amount_total, 32)

    def test_round_globally_round_down_false(self):
        company = self.company
        company.tax_calculation_rounding_method = "round_globally"
        self.assertEqual(company.need_tax_round_down, False)
        invoice = self._create_invoice()
        self.assertEqual(invoice.amount_tax, 2)
        self.assertEqual(invoice.amount_total, 17)
        invoice.write(
            {
                "invoice_line_ids": [Command.create(self._prepare_invoice_line_vals())],
            }
        )
        self.assertEqual(invoice.amount_tax, 3)
        self.assertEqual(invoice.amount_total, 33)
        invoice.write(
            {
                "invoice_line_ids": [Command.create(self._prepare_invoice_line_vals())],
            }
        )
        self.assertEqual(invoice.amount_tax, 5)
        self.assertEqual(invoice.amount_total, 50)

    def test_round_globally_round_down_true(self):
        company = self.company
        company.tax_calculation_rounding_method = "round_globally"
        company.need_tax_round_down = True
        invoice = self._create_invoice()
        self.assertEqual(invoice.amount_tax, 1)
        self.assertEqual(invoice.amount_total, 16)
        invoice.write(
            {
                "invoice_line_ids": [Command.create(self._prepare_invoice_line_vals())],
            }
        )
        self.assertEqual(invoice.amount_tax, 3)
        self.assertEqual(invoice.amount_total, 33)
        invoice.write(
            {
                "invoice_line_ids": [Command.create(self._prepare_invoice_line_vals())],
            }
        )
        self.assertEqual(invoice.amount_tax, 4)
        self.assertEqual(invoice.amount_total, 49)
