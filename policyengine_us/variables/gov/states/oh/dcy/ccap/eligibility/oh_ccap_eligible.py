from policyengine_us.model_api import *


class oh_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Ohio CCAP"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-01",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-03",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-02",
        "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners/Rules%20and%20Resources/2025/PL_21.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.oh.dcy.ccap
        if not p.in_effect:
            return np.zeros_like(
                spm_unit("spm_unit_size", period.this_year), dtype=bool
            )
        p_ccdf = parameters(period).gov.hhs.ccdf
        has_eligible_child = add(spm_unit, period, ["oh_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("oh_ccap_income_eligible", period)
        activity_eligible = spm_unit("oh_ccap_activity_eligible", period)
        asset_eligible = (
            add(spm_unit, period.this_year, ["bank_account_assets"])
            <= p_ccdf.asset_limit
        )
        protective_care = spm_unit("oh_ccap_protective_care", period)
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        standard_eligible = income_eligible & asset_eligible & activity_eligible
        # 5180:6-1-02(G)(1): protective care waives the income, asset, and
        # activity tests; (H)(2): homeless families are exempt from the income
        # and activity requirements but remain subject to the asset test.
        homeless_eligible = is_homeless & asset_eligible
        return has_eligible_child & (
            standard_eligible | protective_care | homeless_eligible
        )
