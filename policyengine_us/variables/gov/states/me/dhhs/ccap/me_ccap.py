from policyengine_us.model_api import *


class me_ccap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine Child Care Affordability Program benefit"
    unit = USD
    definition_period = MONTH
    defined_for = "me_ccap_eligible"
    reference = "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=26"

    def formula(spm_unit, period, parameters):
        parent_fee = spm_unit("me_ccap_parent_fee", period)

        person = spm_unit.members
        is_eligible_child = person("me_ccap_eligible_child", period)
        weekly_market_rate = person("me_ccap_market_rate", period)
        weekly_to_monthly = WEEKS_IN_YEAR / MONTHS_IN_YEAR
        max_reimbursement = (
            spm_unit.sum(weekly_market_rate * is_eligible_child) * weekly_to_monthly
        )

        actual_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        uncapped_benefit = max_(actual_expenses - parent_fee, 0)
        return min_(uncapped_benefit, max_reimbursement)
