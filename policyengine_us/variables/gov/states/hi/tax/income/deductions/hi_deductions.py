from policyengine_us.model_api import *


class hi_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii deductions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15"  # Itemized Deduction
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"  # Standard Deduction
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized

        standard_deduction = tax_unit("hi_standard_deduction", period)
        itemized_deduction = tax_unit("hi_itemized_deduction", period)
        hi_agi = tax_unit("hi_agi", period)
        filing_status = tax_unit("filing_status", period)

        # check itemized deduction eligibility
        filing_status_eligible = (
            itemized_deduction > p.floor.filing_status[filing_status]
        )
        is_dependent = tax_unit("dsi", period)
        standard_cap = min_(hi_agi, standard_deduction)
        dependent_floor = max_(p.floor.dependent, standard_cap)
        dependent_eligible = is_dependent & (
            itemized_deduction > dependent_floor
        )

        return where(
            filing_status_eligible | dependent_eligible,
            itemized_deduction,
            standard_deduction,
        )
