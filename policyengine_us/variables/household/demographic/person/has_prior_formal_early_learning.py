from policyengine_us.model_api import *


class has_prior_formal_early_learning(Variable):
    value_type = bool
    entity = Person
    label = "Has previously participated in formal early learning"
    definition_period = YEAR
    documentation = "Whether the child has previously participated in a formal early learning program (e.g., Head Start, preschool, licensed childcare)"
