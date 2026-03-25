from policyengine_us.model_api import *


class ri_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Rhode Island CCAP benefit amount"
    definition_period = MONTH
    defined_for = "ri_ccap_eligible"
    reference = "https://rules.sos.ri.gov/regulations/part/218-20-00-4"

    def formula(spm_unit, period, parameters):
        copay = spm_unit("ri_ccap_copay", period)
        maximum_weekly_benefit = add(
            spm_unit, period, ["ri_ccap_maximum_weekly_benefit"]
        )
        maximum_monthly_benefit = maximum_weekly_benefit * (
            WEEKS_IN_YEAR / MONTHS_IN_YEAR
        )
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        uncapped = max_(pre_subsidy_childcare_expenses - copay, 0)
        return min_(uncapped, maximum_monthly_benefit)
