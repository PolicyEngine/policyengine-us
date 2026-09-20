from policyengine_us.model_api import *


class de_poc_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Delaware Purchase of Care family copayment"
    definition_period = MONTH
    defined_for = StateCode.DE
    reference = (
        "https://dhss.delaware.gov/wp-content/uploads/sites/2/dss/pdf/PurchaseofCareProviderHandbook_FINAL1_25_2023.pdf#page=95",
        "https://dhss.delaware.gov/dss/childcr/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.de.dss.poc.copay
        countable_income = spm_unit("de_poc_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        fpl_ratio = where(fpg > 0, countable_income / fpg, 0)
        person = spm_unit.members
        has_referred_child = spm_unit.any(
            person("de_poc_has_dfs_referral", period)
            & person("de_poc_eligible_child", period)
        )
        return where(
            (fpl_ratio <= p.waiver_fpl_rate) | has_referred_child,
            0,
            countable_income * p.rate,
        )
