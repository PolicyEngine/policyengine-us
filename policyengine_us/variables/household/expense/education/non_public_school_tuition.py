from policyengine_us.model_api import *


class non_public_school_tuition(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Nonchartered, Nonpublic School Tuition"
