from policyengine_us.model_api import *


class id_iccp(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Idaho Child Care Program benefit amount"
    defined_for = "id_iccp_eligible"
    reference = "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=15"

    def formula(spm_unit, period, parameters):
        maximum_monthly_benefit = add(
            spm_unit, period, ["id_iccp_maximum_monthly_benefit"]
        )
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        capped_expenses = min_(pre_subsidy_childcare_expenses, maximum_monthly_benefit)
        return max_(capped_expenses - spm_unit("id_iccp_copay", period), 0)
