from policyengine_us.model_api import *


class has_cervical_cancer_diagnosis(Variable):
    value_type = bool
    entity = Person
    label = "Has cervical cancer diagnosis"
    documentation = (
        "Whether the person has been diagnosed with cervical cancer."
    )
    definition_period = YEAR
