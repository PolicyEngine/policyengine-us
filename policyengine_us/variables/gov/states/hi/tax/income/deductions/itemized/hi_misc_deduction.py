from policyengine_us.model_api import *


class hi_misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii miscellaneous itemized deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        # Worksheet A-6, lines 23 to 29.
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=34",
        "https://data.capitol.hawaii.gov/sessions/session2026/bills/HB2329_CD1_.pdf#page=17",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized
        if not p.miscellaneous_deductions_allowed:
            return 0
        # Hawaii applies the section 67(a) floor to Hawaii AGI.
        floor_rate = parameters(period).gov.irs.deductions.itemized.misc.floor
        expenses = tax_unit("total_misc_deductions", period)
        hi_agi = tax_unit("hi_agi", period)
        floor = max_(0, hi_agi * floor_rate)
        repayment = tax_unit("hi_claim_of_right_repayment", period)
        section_1341_eligible = tax_unit(
            "hi_claim_of_right_section_1341_eligible", period
        )
        miscellaneous_repayment = where(section_1341_eligible, 0, repayment)
        # Worksheet A-6 pools these expenses with miscellaneous repayments.
        # hi_claim_of_right_deduction already includes the repayment's own
        # allowance, so add only the increase from the other expenses.
        pooled_deduction = max_(0, expenses + miscellaneous_repayment - floor)
        repayment_deduction = max_(0, miscellaneous_repayment - floor)
        return pooled_deduction - repayment_deduction
