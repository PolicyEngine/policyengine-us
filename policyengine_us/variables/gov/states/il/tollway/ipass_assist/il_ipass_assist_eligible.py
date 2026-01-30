from policyengine_us.model_api import *


class il_ipass_assist_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Illinois I-PASS Assist eligible"
    reference = (
        "https://agency.illinoistollway.com/assist",
        "https://www.dhs.state.il.us/page.aspx?item=150431",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("il_ipass_assist_income_eligible", period)
        categorical_eligible = spm_unit(
            "il_ipass_assist_categorical_eligible", period
        )
        return income_eligible | categorical_eligible
