from policyengine_us.model_api import *


class ny_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        itemized_max = tax_unit("ny_itemized_deductions_max", period)
        phase_out = tax_unit("ny_itemized_deductions_phase_out", period)
        reduction = tax_unit("ny_itemized_deductions_reduction", period)
        reduced_deductions = itemized_max - phase_out - reduction

        p = parameters(period).gov.states.ny.tax.income.deductions.itemized.reduction
        agi = tax_unit("ny_agi", period)
        charitable_deduction = tax_unit("charitable_deduction", period)
        charitable_share = charitable_deduction * p.charitable_deduction_rate.calc(agi)
        # Under NY Tax Law § 615(g) and Form IT-196 Line 47, filers with NY AGI
        # over $1,000,000 have their total allowable itemized deduction set directly
        # to 50% (or 25% if NY AGI > $10,000,000) of their federal charitable deduction.
        charitable_rule_applies = tax_unit(
            "ny_itemized_deductions_reduction_based_on_charitable_deduction_applies",
            period,
        )
        return where(
            charitable_rule_applies,
            charitable_share,
            reduced_deductions,
        )
