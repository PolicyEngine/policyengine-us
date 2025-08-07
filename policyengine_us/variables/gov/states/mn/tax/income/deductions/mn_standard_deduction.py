from policyengine_us.model_api import *


class mn_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        # Calculate standard deduction base amount and any additional amount for aged/blind
        p = parameters(period).gov.states.mn.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        lower_reduction_rate = p.reduction.excess_agi_fraction.low
        lower_reduction_threshold = p.reduction.agi_threshold.low[
            filing_status
        ]
        agi = tax_unit("adjusted_gross_income", period)
        lower_excess = max_(0, agi - lower_reduction_threshold)
        base_amt = p.base[filing_status]
        aged_blind_count = tax_unit("aged_blind_count", period)
        extra_amt = aged_blind_count * p.extra[filing_status]
        std_ded = base_amt + extra_amt
        alternate_reduction_amount = p.reduction.alternate.rate * std_ded
        if p.reduction.alternate_reduction_applies:
            higher_reduction_threshold = p.reduction.agi_threshold.high[
                filing_status
            ]

            spread = higher_reduction_threshold - lower_reduction_threshold
            lower_reduction_amount = lower_reduction_rate * min_(
                lower_excess, spread
            )
            higher_reduction_rate = p.reduction.excess_agi_fraction.high
            higher_excess = max_(0, agi - higher_reduction_threshold)
            higher_reduction_amount = higher_reduction_rate * higher_excess
            main_reduction_amount = (
                lower_reduction_amount + higher_reduction_amount
            )
            alternate_reduction_applies = (
                agi > p.reduction.alternate.income_threshold
            )
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
