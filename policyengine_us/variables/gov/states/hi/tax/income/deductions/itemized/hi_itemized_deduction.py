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
        # Cap: $166,800 ($83,400 if married filing separately)
        # You may not be able to deduct all of your itemized deductions if agi reach the cap
        # need to calculate the reduced itemized deductions
        hi_agi = tax_unit("hi_agi", period)
        filing_status = tax_unit("filing_status", period)
        total_itemized_deductions = hi_agi < p.cap.agi_cap[filing_status]
        itemized_deduction = where(
            total_itemized_deductions,
            tax_unit("hi_total_itemized_deduction", period),
            tax_unit("hi_reduced_itemized_deduction", period),
        )
        standard_deduction = tax_unit("hi_standard_deduction", period)

        # check itemized deduction eligibility
        filing_status_eligible = (
            itemized_deduction > p.eligible.filing_status_floor[filing_status]
        )
        is_dependent = tax_unit("dsi", period)
        standard_cap = min_(hi_agi, standard_deduction)
        dependent_floor = max_(p.eligible.dependent_floor, standard_cap)
        dependent_eligible = is_dependent & (
            itemized_deduction > dependent_floor
        )

        return where(
            filing_status_eligible | dependent_eligible,
            itemized_deduction,
            standard_deduction,
        )
