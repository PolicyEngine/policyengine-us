from policyengine_us.model_api import *


class ca_in_medical_care_facility(Variable):
    value_type = bool
    entity = Person
    label = "Is in a California medical care facility"
    definition_period = YEAR
    defined_for = StateCode.CA
