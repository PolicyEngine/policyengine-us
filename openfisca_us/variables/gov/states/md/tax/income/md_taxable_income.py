from openfisca_us.model_api import *


class md_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD taxable income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        md_agi = tax_unit("md_agi", period)
        deductions_exemptions = add(
            tax_unit, period, ["md_deductions", "md_exemptions"]
        )
        return max_(0, md_agi - deductions_exemptions)
