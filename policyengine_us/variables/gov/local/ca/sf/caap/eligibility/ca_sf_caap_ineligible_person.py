from policyengine_us.model_api import *


class ca_sf_caap_ineligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Ineligible person for San Francisco County CAAP"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(person, period, parameters):
        # A person receiving SSI is excluded from CAAP; SSIP serves SSI-pending
        # (not-yet-receiving) applicants (SEC. 20.7-14). SSI is person-level, so
        # only the individual receiving it is excluded.
        receives_ssi = person("ssi", period) > 0
        immigration_status_eligible = person(
            "ca_sf_caap_immigration_status_eligible", period
        )
        return receives_ssi | ~immigration_status_eligible
