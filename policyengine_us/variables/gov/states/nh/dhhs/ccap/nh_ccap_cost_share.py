from policyengine_us.model_api import *


class nh_ccap_cost_share(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "New Hampshire Child Care Scholarship Program weekly family cost share"
    definition_period = MONTH
    defined_for = StateCode.NH
    reference = (
        "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.18",
        "https://www.dhhs.nh.gov/sr_htm/html/sr_24-08_dated_01_24.htm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ccap.cost_share
        countable_income = spm_unit("nh_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        weeks_per_month = WEEKS_IN_YEAR / MONTHS_IN_YEAR

        fpg_ratio = where(fpg > 0, countable_income / fpg, 0)
        income_based_share = (
            countable_income * p.income_share_rate.calc(fpg_ratio) / weeks_per_month
        )
        return p.weekly_flat_amount.calc(fpg_ratio) + income_based_share
