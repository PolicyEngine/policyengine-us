from policyengine_us.model_api import *


class is_optional_senior_or_disabled_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Seniors or disabled people not meeting SSI rules"
    documentation = "Whether this person qualifies for Medicaid through the State's optional aged, blind, or disabled pathway (not otherwise SSI-eligible)"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#m"

    def formula(person, period, parameters):
        is_senior_or_disabled = person("is_ssi_aged_blind_disabled", period)
        income_eligible = person(
            "is_optional_senior_or_disabled_income_eligible", period
        )
        asset_eligible = person(
            "is_optional_senior_or_disabled_asset_eligible", period
        )
        return is_senior_or_disabled & income_eligible & asset_eligible
