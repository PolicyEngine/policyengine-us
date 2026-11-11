from policyengine_us.model_api import *


class ny_itemized_deductions_lower_incremental_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York itemized deductions lower incremental reduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",  # (f)
        "https://www.tax.ny.gov/pdf/2021/inc/it196_2021.pdf#page=3",  # Lines 40-49
        "https://www.tax.ny.gov/pdf/2021/inc/it196i_2021.pdf#page=20",  # Line 46
    )
    defined_for = "ny_itemized_deductions_reduction_applies"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.deductions.itemized.reduction.incremental.lower
        agi = tax_unit("ny_agi", period)
        filing_status = tax_unit("filing_status", period)
        agi_excess = max_(agi - p.income_threshold[filing_status], 0)
        numerator = min_(p.numerator, agi_excess)
        fraction = numerator / p.denominator
        # Tax Law 615(f) applies the percentage to the New York itemized
        # deduction otherwise allowable under 615(a): the pre-TCJA federal
        # deductions after the line 40 limitation, with the 615(c)-(e)
        # modifications, including the 615(d)(4) college tuition deduction.
        # This is IT-196 line 45 for Form IT-203 filers (line 43 tuition).
        itemized_max = tax_unit("ny_itemized_deductions_max", period)
        phase_out = tax_unit("ny_itemized_deductions_phase_out", period)
        base = itemized_max - phase_out
        return base * p.rate * fraction
