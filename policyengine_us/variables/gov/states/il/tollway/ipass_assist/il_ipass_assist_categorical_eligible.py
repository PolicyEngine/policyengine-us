from policyengine_us.model_api import *


class il_ipass_assist_categorical_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Illinois I-PASS Assist categorically eligible"
    reference = [
        "https://agency.illinoistollway.com/assist",
        "https://www.dhs.state.il.us/page.aspx?item=150431",
    ]
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        # Per IL DHS: "Customers getting SNAP may be eligible for I-PASS Assist"
        return spm_unit("snap", period) > 0
