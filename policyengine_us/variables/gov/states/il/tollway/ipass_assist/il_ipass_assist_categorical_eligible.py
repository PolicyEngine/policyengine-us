from policyengine_us.model_api import *


class il_ipass_assist_categorical_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Illinois I-PASS Assist categorically eligible"
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=150431",
        "https://agency.illinoistollway.com/documents/20184/1344218/2023-06_IPASS%20Assist%20One%20Pager.pdf/11051bbf-1809-6d1b-de08-90ba3d931b23#page=1",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        # IL Tollway: eligible if "currently participating in SNAP or TANF"
        snap = spm_unit("snap", period) > 0
        tanf = spm_unit("il_tanf", period) > 0
        return snap | tanf
