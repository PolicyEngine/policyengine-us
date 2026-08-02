from policyengine_us.model_api import *


class ny_ccap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "New York Child Care Assistance Program benefit"
    unit = USD
    defined_for = StateCode.NY
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=39",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        market_rate = person("ny_ccap_market_rate", period)
        eligible = person("is_ccdf_eligible", period.this_year)
        total_eligible_market_rate = spm_unit.sum(market_rate * eligible)
        childcare_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        reimbursable_care = min_(
            childcare_expenses,
            total_eligible_market_rate,
        )
        family_share = spm_unit("ny_ccap_family_share", period)
        # New York's own income limit (300% of the poverty guideline, then
        # 85% of the state median income) binds below the federal 85% state
        # median income ceiling embedded in is_ccdf_eligible.
        income_eligible = spm_unit("ny_ccap_income_eligible", period)
        return income_eligible * max_(reimbursable_care - family_share, 0)
