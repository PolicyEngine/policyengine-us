from policyengine_us.model_api import *


class hi_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii deductions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15\n"  # Itemized Deduction
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"  # Standard Deduction
    )
    reference = (
        # Act 35, SLH 2026 conforms to sections 170(p) and 224 from 2026.
        "https://data.capitol.hawaii.gov/sessions/session2026/bills/HB2329_CD1_.pdf#page=1",
        "https://files.hawaii.gov/tax/news/announce/ann26-06.pdf#page=2",
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p_deductions = parameters(period).gov.states.hi.tax.income.deductions
        p = p_deductions.itemized

        standard_deduction = tax_unit("hi_standard_deduction", period)
        total_itemized_deduction = tax_unit("hi_itemized_deductions", period)
        tax_unit_earned_income = tax_unit("tax_unit_earned_income", period)
        filing_status = tax_unit("filing_status", period)

        # check itemized deduction eligibility
        filing_status_eligible = (
            total_itemized_deduction > p.threshold.deductions[filing_status]
        )
        is_dependent_on_another_return = tax_unit("head_is_dependent_elsewhere", period)
        standard_cap = min_(tax_unit_earned_income, standard_deduction)
        dependent_floor = max_(p.threshold.dependent, standard_cap)
        dependent_eligible = is_dependent_on_another_return & (
            total_itemized_deduction > dependent_floor
        )
        itemized_deductions_eligible = filing_status_eligible | dependent_eligible
        itemized_deduction = where(
            itemized_deductions_eligible, total_itemized_deduction, 0
        )
        # Section 170(p) lets taxpayers who do not itemize deduct some cash
        # charitable contributions on top of the standard deduction.
        non_itemizer_charitable_deduction = (
            tax_unit("charitable_deduction_for_non_itemizers", period)
            if p_deductions.non_itemizer_charitable.in_effect
            else 0
        )
        # Section 224 allows the qualified tips deduction whether or not the
        # taxpayer itemizes.
        tip_income_deduction = tax_unit("hi_tip_income_deduction", period)
        return (
            max_(
                itemized_deduction,
                standard_deduction + non_itemizer_charitable_deduction,
            )
            + tip_income_deduction
        )
