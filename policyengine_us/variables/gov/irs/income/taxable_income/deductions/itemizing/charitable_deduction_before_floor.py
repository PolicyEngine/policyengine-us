from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.deductions.itemizing.charitable_deduction import (
    compute_charitable_deduction_before_floor,
)


class charitable_deduction_before_floor(Variable):
    value_type = float
    entity = TaxUnit
    label = "Charitable deduction before the federal floor"
    unit = USD
    documentation = "Charitable contributions after federal percentage ceilings and before the federal contribution-base floor."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170"

    def formula(tax_unit, period, parameters):
        return compute_charitable_deduction_before_floor(tax_unit, period, parameters)
