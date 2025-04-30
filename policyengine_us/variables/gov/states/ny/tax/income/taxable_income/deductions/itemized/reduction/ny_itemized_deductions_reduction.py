from policyengine_us.model_api import *


class ny_itemized_deductions_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY itemized deductions reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"  # (f)&(g)
    defined_for = "ny_itemized_deductions_reduction_applies"

    def formula(tax_unit, period, parameters):
        reduction_based_on_charitable_deduction_applies = tax_unit(
            "ny_itemized_deductions_reduction_based_on_charitable_deduction_applies",
            period,
        )
        reduction_based_on_charitable_deduction = tax_unit(
            "ny_itemized_deductions_reduction_based_on_charitable_deduction",
            period,
        )
        incremental_reduction = tax_unit(
            "ny_itemized_deductions_incremental_reduction", period
        )
        return where(
            reduction_based_on_charitable_deduction_applies,
            reduction_based_on_charitable_deduction,
            incremental_reduction,
        )
