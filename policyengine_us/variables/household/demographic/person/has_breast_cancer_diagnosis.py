from policyengine_us.model_api import *


class has_breast_cancer_diagnosis(Variable):
    value_type = bool
    entity = Person
    label = "Has breast cancer diagnosis"
    documentation = "Whether the person has been diagnosed with breast cancer."
    definition_period = YEAR
