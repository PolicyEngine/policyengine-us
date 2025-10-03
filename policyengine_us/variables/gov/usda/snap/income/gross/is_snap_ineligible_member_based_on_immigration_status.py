from policyengine_us.model_api import *


class is_snap_ineligible_member_based_on_immigration_status(Variable):
    value_type = bool
    entity = Person
    label = "Person ineligible for SNAP based on immigration status"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_3"

    def formula(person, period, parameters):
        immigration_status_eligible = person(
            "snap_immigration_status_eligible_person", period
        )

        return ~immigration_status_eligible
