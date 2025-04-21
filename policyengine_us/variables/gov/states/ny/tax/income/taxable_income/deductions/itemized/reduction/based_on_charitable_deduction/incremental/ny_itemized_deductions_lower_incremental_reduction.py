from policyengine_us.model_api import *


class ny_itemized_deductions_lower_incremental_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York itemized deductions lower incremental reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"  # (f)
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
        itemized_deduction = tax_unit("ny_itemized_deductions_max", period)
        return itemized_deduction * p.rate * fraction
