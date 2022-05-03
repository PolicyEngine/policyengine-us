from openfisca_us.model_api import *


class pre_qbid_taxinc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable income (pre-QBID)"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        ui_amount = tax_unit("tax_unit_ui", period)
        agi = tax_unit("c00100", period)
        ui_excluded = ui_amount - tax_unit("taxable_ui", period)
        maximum_deduction = max_(
            tax_unit("c04470", period), tax_unit("standard", period)
        )
        personal_exemptions = tax_unit("c04600", period)
        return max_(
            0, agi - maximum_deduction - personal_exemptions - ui_excluded
        )


class c04800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable income"
    documentation = "Regular taxable income"
    unit = USD

    def formula(tax_unit, period, parameters):
        return max_(
            0, tax_unit("pre_qbid_taxinc", period) - tax_unit("qbided", period)
        )


taxable_income = variable_alias("taxable_income", c04800)
