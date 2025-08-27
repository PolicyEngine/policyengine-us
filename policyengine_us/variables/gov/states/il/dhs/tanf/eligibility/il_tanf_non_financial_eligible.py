from policyengine_us.model_api import *


class il_tanf_non_financial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Illinois Temporary Assistance for Needy Families (TANF) due to non financial requirements"
    definition_period = MONTH
    reference = "https://www.dhs.state.il.us/page.aspx?item=30358"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        demographic_eligible = (
            add(spm_unit, period, ["il_tanf_demographic_eligible_person"]) > 0
        )
        immigration_status_eligible = (
            add(
                spm_unit,
                period,
                ["il_tanf_immigration_status_eligible_person"],
            )
            > 0
        )
        return demographic_eligible & immigration_status_eligible
