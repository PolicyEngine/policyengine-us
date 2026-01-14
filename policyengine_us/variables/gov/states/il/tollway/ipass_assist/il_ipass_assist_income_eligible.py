from policyengine_us.model_api import *


class il_ipass_assist_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Illinois I-PASS Assist income eligible"
    reference = (
        "https://agency.illinoistollway.com/assist",
        "https://www.dhs.state.il.us/page.aspx?item=150431",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.tollway.ipass_assist.eligibility
        fpg = spm_unit("spm_unit_fpg", period)
        # Use gross income (market income + social security) for eligibility
        market_income = spm_unit("spm_unit_market_income", period)
        social_security = add(spm_unit, period, ["social_security"])
        household_income = market_income + social_security
        return household_income <= fpg * p.fpg_limit
