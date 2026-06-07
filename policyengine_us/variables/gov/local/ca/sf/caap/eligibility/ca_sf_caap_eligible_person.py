from policyengine_us.model_api import *


class ca_sf_caap_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Counts toward the San Francisco County CAAP budget unit"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(person, period, parameters):
        # A person counts toward the CAAP budget unit if they are not an SSI
        # recipient and have a qualified immigration status. SSI recipients are
        # served by SSI/SSP (SSIP serves SSI-pending applicants); persons without
        # a qualified immigration status are not eligible (SEC. 20.7-6, 20.7-14).
        # ssi is person-level, so only the SSI individual is excluded.
        receives_ssi = person("ssi", period) > 0
        immigration_status_eligible = person(
            "ca_sf_caap_immigration_status_eligible", period
        )
        return ~receives_ssi & immigration_status_eligible
