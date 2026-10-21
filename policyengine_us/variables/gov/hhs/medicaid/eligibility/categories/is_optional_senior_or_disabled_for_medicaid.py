from policyengine_us.model_api import *


class is_optional_senior_or_disabled_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Seniors or disabled people not meeting SSI rules"
    documentation = "Whether this person qualifies for Medicaid through the State's optional aged, blind, or disabled pathway (not otherwise SSI-eligible)"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#m"

    def formula(person, period, parameters):
        # Some states cover aged, blind, or disabled people as categorically
        # needy only if they receive SSI, and have no group for those who do not.
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled
        covers_group = p.covers_non_ssi_recipients[state].astype(bool)
        is_senior_or_disabled = person("is_ssi_aged_blind_disabled", period)
        income_eligible = person(
            "is_optional_senior_or_disabled_income_eligible", period
        )
        asset_eligible = person("is_optional_senior_or_disabled_asset_eligible", period)
        return covers_group & is_senior_or_disabled & income_eligible & asset_eligible
