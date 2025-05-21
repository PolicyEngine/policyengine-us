from policyengine_us.model_api import *


class ma_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts LIHEAP payment"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-november-2024/download"

    def formula(spm_unit, period, parameters):
        payment_amount = add(
            spm_unit,
            period,
            ["ma_liheap_standard_payment", "ma_liheap_hecs_payment"],
        )

        # This should be heating_oil_and_propane_expense, natural_gas_expense, kerosene_expense, electricity_expense, other_expense,
        # to avoid creating new variables for each heating type, use the existing ones
        actual_expense = add(
            spm_unit,
            period,
            ["heating_cooling_expense", "gas_expense", "electricity_expense"],
        )
        return min_(actual_expense, payment_amount)
