from policyengine_us.model_api import *


class mn_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-12/m1_inst_21.pdf#page=12",
        "https://www.revenue.state.mn.us/sites/default/files/2024-02/m1-inst-22.pdf#page=12",
        "https://www.revenue.state.mn.us/sites/default/files/2025-06/m1-inst-23.pdf#page=13",
        "https://www.revenue.state.mn.us/sites/default/files/2026-01/m1-inst-24.pdf#page=13",
        "https://taxsim.nber.org/historical_state_tax_forms/MN/2025/m1-inst-25_0.pdf#page=13",
        "https://www.revisor.mn.gov/statutes/cite/290.0123",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        # Calculate standard deduction base amount and any additional amount for aged/blind
        p = parameters(period).gov.states.mn.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        lower_reduction_rate = p.reduction.excess_agi_fraction.low
        lower_reduction_threshold = p.reduction.agi_threshold.low[filing_status]
        agi = tax_unit("adjusted_gross_income", period)
        lower_excess = max_(0, agi - lower_reduction_threshold)
        base_amt = p.base[filing_status]
        aged_blind_count = tax_unit("aged_blind_count", period)
        extra_amt = aged_blind_count * p.extra[filing_status]
        # Minn. Stat. 290.0123 subd. 3 limits the standard deduction of a
        # dependent of another taxpayer. The Form M1 Worksheet for Line 4 —
        # Dependent Standard Deduction applies "only if someone can claim
        # you, or your spouse if filing a joint return, as a dependent":
        # step 1 is the greater of the floor or earned income plus the
        # addition, and steps 2-5 cap it at the single (subd. 1, clause (3))
        # amount plus the aged and blind amounts for the filing status. The
        # limitation worksheet below then reduces that amount.
        dependent_elsewhere = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        # Worksheet earned income: wages and self-employment income minus the
        # deductible part of self-employment tax (Schedule 1, line 15).
        earned_income = max_(
            tax_unit("tax_unit_earned_income", period)
            - tax_unit("self_employment_tax_ald", period),
            0,
        )
        dependent_amount = min_(
            max_(
                earned_income + p.dependent.additional_earned_income, p.dependent.amount
            ),
            p.base["SINGLE"] + extra_amt,
        )
        std_ded = where(dependent_elsewhere, dependent_amount, base_amt + extra_amt)
        alternate_reduction_amount = p.reduction.alternate.rate * std_ded
        if p.reduction.alternate_reduction_applies:
            higher_reduction_threshold = p.reduction.agi_threshold.high[filing_status]

            spread = higher_reduction_threshold - lower_reduction_threshold
            lower_reduction_amount = lower_reduction_rate * min_(lower_excess, spread)
            higher_reduction_rate = p.reduction.excess_agi_fraction.high
            higher_excess = max_(0, agi - higher_reduction_threshold)
            higher_reduction_amount = higher_reduction_rate * higher_excess
            main_reduction_amount = lower_reduction_amount + higher_reduction_amount
            alternate_reduction_applies = agi > p.reduction.alternate.income_threshold
            smaller_reduction_amount = min_(
                alternate_reduction_amount, main_reduction_amount
            )
            reduction = where(
                alternate_reduction_applies,
                alternate_reduction_amount,
                smaller_reduction_amount,
            )
        else:
            # ... calculate pre-limitation amount
            excess_agi = max_(0, agi - lower_reduction_threshold)
            main_reduction_amount = lower_reduction_rate * excess_agi
            reduction = min_(alternate_reduction_amount, main_reduction_amount)
        return max_(0, std_ded - reduction)
