from policyengine_us.model_api import *


class ga_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/it-511-individual-income-tax-booklet"
        # above reference provides access to booklets for all years
        # definition of Georgia taxable income starts on page 12
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ga_agi", period)
        deductions = tax_unit("ga_deductions", period)
        exemptions = tax_unit("ga_exemptions", period)
        return max_(0, agi - deductions - exemptions)
