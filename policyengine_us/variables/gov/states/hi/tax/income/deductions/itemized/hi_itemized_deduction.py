from policyengine_us.model_api import *


class hi_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii itemized deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32"  # total itemized deduction worksheet
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized

        # Hawaii did not suspend the overall limitation on itemized deductions
        # You may not be able to deduct all of your itemized deductions if agi reach the cap
        # need to calculate the reduced itemized deductions
        hi_agi = tax_unit("hi_agi", period)
        filing_status = tax_unit("filing_status", period)
        total_itemized_deductions = hi_agi < p.cap.agi[filing_status]

        return where(
            total_itemized_deductions,
            tax_unit("hi_total_itemized_deduction", period),
            tax_unit("hi_reduced_itemized_deduction", period),
        )
