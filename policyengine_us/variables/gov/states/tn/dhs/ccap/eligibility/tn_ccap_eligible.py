from policyengine_us.model_api import *


class tn_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Tennessee CCAP"
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = (
        "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=36",
        "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=32",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["tn_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("tn_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("tn_ccap_activity_eligible", period)
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        person = spm_unit.members
        has_protective_child = (
            spm_unit.sum(
                person("tn_ccap_eligible_child", period)
                * person("receives_or_needs_protective_services", period.this_year)
            )
            > 0
        )
        protective_services_waiver = spm_unit(
            "tn_ccap_protective_services_waiver", period
        )
        # Protective-services cases are not evaluated for income or assets
        # (State Plan §2.2.6(b)) and have no activity requirement (§2.2.2.g/h).
        income_activity_asset_waived = has_protective_child & protective_services_waiver
        income_activity_eligible = income_eligible & activity_eligible
        return has_eligible_child & (
            income_activity_asset_waived
            | (asset_eligible & (income_activity_eligible | tanf_enrolled))
        )
