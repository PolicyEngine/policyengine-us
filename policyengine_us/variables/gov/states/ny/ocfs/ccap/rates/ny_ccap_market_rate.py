from policyengine_us.model_api import *


class ny_ccap_market_rate(Variable):
    value_type = float
    entity = Person
    label = "New York CCAP monthly market rate"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NY
    documentation = (
        "Returns the regular monthly rate, including excess care periods "
        "and any legally exempt group enhancement. A child with a disability "
        "receives the special-needs rate only when the parent demonstrates "
        "additional care needs and the child's expense share exceeds the "
        "regular rate, under 18 NYCRR 415.9 and 24-OCFS-LCM-22. Payment "
        "differentials apply separately to the lesser of expenses and this rate."
    )
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.9",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=7",
    )

    def formula(person, period, parameters):
        regular = person("ny_ccap_regular_market_rate", period)
        qualifies = person("ny_ccap_special_needs_rate_eligible", period)
        multiplier = parameters(
            period
        ).gov.states.ny.ocfs.ccap.rates.special_needs_multiplier
        return regular * where(qualifies, multiplier, 1)
