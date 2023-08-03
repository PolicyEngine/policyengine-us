from policyengine_us.model_api import *


class is_ccdf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligibility for CCDF"

    def formula(person, period, parameters):
        asset_eligible = person.spm_unit("is_ccdf_asset_eligible", period)
        age_eligible = person("is_ccdf_age_eligible", period)
        income_eligible = person.spm_unit("is_ccdf_income_eligible", period)
        reason_for_care_eligible = person(
            "is_ccdf_reason_for_care_eligible", period
        )

        return (
            asset_eligible
            & age_eligible
            & income_eligible
            & reason_for_care_eligible
        )
