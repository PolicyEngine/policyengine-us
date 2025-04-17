from policyengine_us.model_api import *


class ny_itemized_deductions_reduction_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether the reduction to the New York itemized deductions applies"
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"  # (f)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.deductions.itemized.reduction.incremental.lower
        agi = tax_unit("ny_agi", period)
        filing_status = tax_unit("filing_status", period)
        lower_income_threshold = p.income_threshold[filing_status]
        # No reduction applies if the AGI is less than the first reduction threshold
        return agi > lower_income_threshold
