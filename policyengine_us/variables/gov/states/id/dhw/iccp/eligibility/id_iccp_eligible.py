from policyengine_us.model_api import *


class id_iccp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for the Idaho Child Care Program"
    defined_for = StateCode.ID
    reference = (
        "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=7",
        "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=12",
        "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=13",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["id_iccp_eligible_child"]) > 0
        return (
            has_eligible_child
            & spm_unit("id_iccp_income_eligible", period)
            & spm_unit("is_ccdf_asset_eligible", period.this_year)
            & spm_unit("id_iccp_activity_eligible", period)
        )
