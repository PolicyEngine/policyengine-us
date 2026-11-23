from policyengine_us.model_api import *


class hi_liheap_disabled_member(Variable):
    value_type = bool
    entity = Person
    label = "Disabled member for Hawaii LIHEAP"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        # PDF pages 2, 8, 20
        "https://humanservices.hawaii.gov/wp-content/uploads/2019/07/Policies-and-Procedures-2020.pdf#page=2",
        "https://humanservices.hawaii.gov/wp-content/uploads/2025/07/Model-Plan-Packet-2026.pdf#page=55",
    )

    def formula(person, period, parameters):
        # The manuals define a disabled individual by receipt of SSI or Social
        # Security disability payments, or "VA benefits for a 100%
        # service-connected disability". Governmental disability retirement
        # and railroad disability have no separate input, so is_disabled
        # stands in for them. The manuals don't say whether a total rating
        # based on individual unemployability counts; the VA flag includes
        # it.
        return (
            person("is_disabled", period)
            | (person("ssi", period) > 0)
            | (add(person, period, ["receives_ssi"]) > 0)
            | (person("social_security_disability", period) > 0)
            | person("is_fully_disabled_service_connected_veteran", period)
        )
