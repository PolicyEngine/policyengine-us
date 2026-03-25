from policyengine_us.model_api import *


class ri_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Rhode Island CCAP"
    definition_period = MONTH
    defined_for = StateCode.RI
    reference = (
        "https://rules.sos.ri.gov/regulations/part/218-20-00-4",
        "https://rules.sos.ri.gov/regulations/part/218-20-00-4#4.5",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["ri_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("ri_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("ri_ccap_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
