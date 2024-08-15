from policyengine_us.model_api import *


class goes_to_medical_or_therapy_visits(Variable):
    value_type = bool
    entity = Person
    label = "Goes to medical or therapy visits"
    definition_period = YEAR
