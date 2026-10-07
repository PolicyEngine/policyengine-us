from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.deductions.itemizing._charitable_deduction_helpers import (
    charitable_deduction_given_contribution_base,
)


class charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Charitable deduction"
    unit = USD
    documentation = "Deduction from taxable income for charitable donations."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170"

    def formula(tax_unit, period, parameters):
        positive_agi = tax_unit("positive_agi", period)
        return charitable_deduction_given_contribution_base(
            tax_unit, period, parameters, positive_agi
        )
