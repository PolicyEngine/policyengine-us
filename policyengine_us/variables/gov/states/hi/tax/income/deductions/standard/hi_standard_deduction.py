from policyengine_us.model_api import *


class hi_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii standard deduction"
    unit = USD
    reference = (
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=11",
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=20",
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions
        status = tax_unit("filing_status", period)
        regular = p.standard.amount[status]
        dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        earned = tax_unit("standard_deduction_worksheet_earned_income", period)
        limited = min_(regular, max_(p.itemized.threshold.dependent, earned))
        required = tax_unit("hi_required_to_itemize", period)
        return where(required, 0, where(dependent, limited, regular))
