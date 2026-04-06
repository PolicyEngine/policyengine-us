from policyengine_us.model_api import *


class de_poc(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Delaware Purchase of Care benefit amount"
    definition_period = MONTH
    defined_for = "de_poc_eligible"
    reference = (
        "https://regulations.delaware.gov/AdminCode/title16/Department%20of%20Health%20and%20Social%20Services/Division%20of%20Social%20Services/11004.shtml",
        "https://dhss.delaware.gov/dss/childcr/",
    )

    def formula(spm_unit, period, parameters):
        copay = spm_unit("de_poc_copay", period)
        maximum_weekly_benefit = add(
            spm_unit, period, ["de_poc_maximum_weekly_benefit"]
        )
        maximum_monthly_benefit = maximum_weekly_benefit * (
            WEEKS_IN_YEAR / MONTHS_IN_YEAR
        )
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        uncapped = max_(pre_subsidy_childcare_expenses - copay, 0)
        return min_(uncapped, maximum_monthly_benefit)
