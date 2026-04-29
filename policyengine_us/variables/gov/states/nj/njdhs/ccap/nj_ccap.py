from policyengine_us.model_api import *


class nj_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "New Jersey CCAP benefit amount"
    definition_period = MONTH
    defined_for = "nj_ccap_eligible"
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-15-5-2",
        "https://www.childcarenj.gov/ChildCareNJ/media/media_library/CCDF_State_Plan_for_New_Jersey_FFY25-27.pdf#page=14",
    )

    def formula(spm_unit, period, parameters):
        copay = spm_unit("nj_ccap_copay", period)
        maximum_weekly_benefit = add(
            spm_unit, period, ["nj_ccap_maximum_weekly_benefit"]
        )
        maximum_monthly_benefit = maximum_weekly_benefit * (
            WEEKS_IN_YEAR / MONTHS_IN_YEAR
        )
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        uncapped = max_(pre_subsidy_childcare_expenses - copay, 0)
        return min_(uncapped, maximum_monthly_benefit)
