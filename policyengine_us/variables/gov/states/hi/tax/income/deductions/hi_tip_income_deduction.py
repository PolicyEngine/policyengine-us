from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.deductions.tip_income.tip_income_deduction import (
    compute_tip_income_deduction,
)


class hi_tip_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii qualified tips deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://data.capitol.hawaii.gov/sessions/session2026/bills/HB2329_CD1_.pdf#page=1",
        "https://files.hawaii.gov/tax/news/announce/ann26-06.pdf#page=3",
        "https://www.law.cornell.edu/uscode/text/26/224",
    )

    def formula(tax_unit, period, parameters):
        if not parameters(
            period
        ).gov.states.hi.tax.income.deductions.tip_income.in_effect:
            return 0
        # HRS 235-1 defines AGI using the chapter 235 modifications.
        # Hawaii makes sections 911, 931 and 933 inoperative, so Hawaii AGI
        # needs no addback for those exclusions under section 224(b)(2)(B).
        hi_agi = tax_unit("hi_agi", period)
        return compute_tip_income_deduction(tax_unit, period, parameters, hi_agi)
