from policyengine_us.model_api import *


class ny_itemized_deductions_higher_incremental_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York itemized deductions higher incremental reduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",  # (f)
        "https://www.tax.ny.gov/pdf/2021/inc/it196i_2021.pdf#page=20",  # Line 46
    )
    defined_for = "ny_itemized_deductions_reduction_applies"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.deductions.itemized.reduction.incremental.higher
        agi = tax_unit("ny_agi", period)
        agi_excess = max_(agi - p.income_threshold, 0)
        numerator = min_(p.numerator, agi_excess)
        fraction = numerator / p.denominator
        # IT-196 line 46 worksheets take a share of line 45, which is after the
        # line 40 limitation and before the college tuition deduction (line 48).
        itemized_max = tax_unit("ny_itemized_deductions_max", period)
        college_tuition = tax_unit("ny_college_tuition_deduction", period)
        phase_out = tax_unit("ny_itemized_deductions_phase_out", period)
        line_45 = max_(itemized_max - college_tuition - phase_out, 0)
        return line_45 * p.rate * fraction
