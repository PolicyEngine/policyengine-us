from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.deductions.itemizing._charitable_deduction_helpers import (
    charitable_deduction_given_contribution_base,
)


class hi_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii charitable deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        # Line 21d and the limits stated as a share of Hawaii AGI.
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=17",
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=18",
        # Act 35, SLH 2026 conforms to the section 170(b)(1)(I) floor.
        "https://files.hawaii.gov/tax/news/announce/ann26-06.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        # The N-11 instructions measure the section 170(b) limits against
        # Hawaii adjusted gross income, so Hawaii AGI is the contribution
        # base for the ceilings and for the 0.5% floor from 2026.
        hi_agi = tax_unit("hi_agi", period)
        return charitable_deduction_given_contribution_base(
            tax_unit, period, parameters, max_(hi_agi, 0)
        )
