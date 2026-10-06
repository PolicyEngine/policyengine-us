from policyengine_us.model_api import *


class hi_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii itemized deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=20",
        # Total Itemized Deductions Worksheet, line 11.
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=34",
    )

    def formula(tax_unit, period, parameters):
        total_deductions = tax_unit("hi_total_itemized_deductions", period)
        reduction = tax_unit("hi_itemized_deductions_reduction", period)
        return max_(0, total_deductions - reduction)
