from policyengine_us.model_api import *


class is_snap_prorate_person(Variable):
    value_type = bool
    entity = Person
    label = "Person in SNAP unit subject to SNAP proration rules"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_3"

    def formula(person, period, parameters):
        immigration_status_eligible = person(
            "snap_immigration_status_eligible_person", period
        )

        return ~immigration_status_eligible
