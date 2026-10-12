from policyengine_us.model_api import *


class ms_ccpp(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Mississippi CCPP benefit amount"
    definition_period = MONTH
    defined_for = "ms_ccpp_eligible"
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=57"

    def formula(spm_unit, period, parameters):
        copay = spm_unit("ms_ccpp_copay", period)
        # Sum the per-child weekly maximum rates and convert to monthly.
        weekly_rate = add(spm_unit, period, ["ms_ccpp_maximum_weekly_rate"])
        monthly_rate = weekly_rate * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        # The subsidy covers the lesser of the provider's charge and the
        # maximum rate, net of the family co-payment.
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        capped_expenses = min_(pre_subsidy_childcare_expenses, monthly_rate)
        return max_(capped_expenses - copay, 0)
