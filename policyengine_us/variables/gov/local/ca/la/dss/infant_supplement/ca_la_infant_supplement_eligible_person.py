from policyengine_us.model_api import *


class ca_la_infant_supplement_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible for the Los Angeles County infant supplement"
    defined_for = "in_la"

    def formula(person, period, parameters):
        is_parent = person("is_pregnant", period)
        # Needed as numeric yearly variables get divided by 12 in monthly formulas.
        foster_care_minor_dependent = person(
            "ca_foster_care_minor_dependent", period
        )
        return foster_care_minor_dependent & is_parent
