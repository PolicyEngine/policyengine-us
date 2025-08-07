from policyengine_us.model_api import *


class ny_itemized_deductions_reduction_based_on_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "New York itemized deductions reduction based on charitable deduction"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/2024/inc/it196i_2024.pdf#page=20"  # Line 46, worksheet 5 & 6
    defined_for = "ny_itemized_deductions_reduction_based_on_charitable_deduction_applies"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.deductions.itemized.reduction
        agi = tax_unit("ny_agi", period)
        charitable_deduction = tax_unit("charitable_deduction", period)
        applicable_rate = p.charitable_deduction_rate.calc(agi)
        max_deduction = tax_unit("ny_itemized_deductions_max", period)
        total_reduction_amount = charitable_deduction * applicable_rate
        return max_(max_deduction - total_reduction_amount, 0)
