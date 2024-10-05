from policyengine_us.model_api import *


class nj_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey taxable income"
    unit = USD
    documentation = "NJ AGI less taxable income deductions (Line 42)"
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3-1/"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get taxable income before property tax deduction or credit.
        taxable_income_before_deduction = tax_unit(
            "nj_taxable_income_before_property_tax_deduction", period
        )

        # Get the property tax deduction.
        property_tax_deduction = tax_unit("nj_property_tax_deduction", period)

        return max_(
            0, taxable_income_before_deduction - property_tax_deduction
        )
