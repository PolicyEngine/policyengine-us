from policyengine_us.model_api import *


class ma_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts LIHEAP payment"
    definition_period = YEAR
    defined_for = "ma_liheap_eligible"
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download"

    def formula(spm_unit, period, parameters):
        payment_amount = add(
            spm_unit,
            period,
            ["ma_liheap_standard_payment", "ma_liheap_hecs_payment"],
        )
        actual_expense_amount = add(
            spm_unit,
            period,
            ["heating_cooling_expense", "gas_expense", "electricity_expense"],
        )
        return min_(actual_expense_amount, payment_amount)
