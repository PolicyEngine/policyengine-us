from policyengine_us.model_api import *


class ny_itemized_deductions_reduction_based_on_charitable_deduction_applies(
    Variable
):
    value_type = bool
    entity = TaxUnit
    label = (
        "New York itemized deductions reduction based on charitable deduction"
    )
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"  # (g)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.deductions.itemized.reduction
        agi = tax_unit("ny_agi", period)
        high_income_threshold = p.charitable_deduction_rate.thresholds[1]
        return agi > high_income_threshold
