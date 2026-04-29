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
        # Heat-in-rent is a direct subsidy — no expense cap.
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        actual_expense_amount = add(spm_unit, period, ["heating_expense_person"])
        return where(
            heat_in_rent,
            payment_amount,
            min_(actual_expense_amount, payment_amount),
        )
