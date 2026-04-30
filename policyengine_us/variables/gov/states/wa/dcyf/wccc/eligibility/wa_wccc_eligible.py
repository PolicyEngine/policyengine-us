from policyengine_us.model_api import *


class wa_wccc_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Washington Working Connections Child Care"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0005",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0023",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["wa_wccc_eligible_child"]) > 0
        income_eligible = spm_unit("wa_wccc_income_eligible", period)
        resources_eligible = spm_unit("wa_wccc_resources_eligible", period)
        activity_eligible = spm_unit("wa_wccc_activity_eligible", period)
        categorical_eligible = spm_unit("wa_wccc_categorical_eligible", period)
        standard_path = income_eligible & resources_eligible & activity_eligible
        return has_eligible_child & (standard_path | categorical_eligible)
