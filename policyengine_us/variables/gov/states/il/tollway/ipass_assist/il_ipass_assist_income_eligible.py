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
        # Income verified by Illinois Department of Revenue
        gross_income = add(spm_unit, period, ["irs_gross_income"])
        return gross_income <= fpg * p.fpg_limit
