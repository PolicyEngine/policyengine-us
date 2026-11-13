from policyengine_us.model_api import *


class ny_ccap_special_needs_rate_eligible(Variable):
    value_type = bool
    entity = Person
    label = "New York CCAP special-needs market rate eligible"
    definition_period = MONTH
    defined_for = StateCode.NY
    documentation = (
        "A child with a disability receives the special-needs market rate "
        "when the parent demonstrates additional care needs and the child's "
        "expense share exceeds the regular rate, under 18 NYCRR 415.9 and "
        "24-OCFS-LCM-22."
    )
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.9",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=7",
    )

    def formula(person, period, parameters):
        disabled = person("is_disabled", period.this_year)
        additional_care = person("ny_ccap_special_needs_care", period.this_year)
        expenses = person("ny_ccap_childcare_expenses", period)
        regular = person("ny_ccap_regular_market_rate", period)
        return disabled & additional_care & (expenses > regular)
