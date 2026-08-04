from policyengine_us.model_api import *


class attends_eligible_educational_institution_for_lifetime_learning_credit(Variable):
    value_type = bool
    entity = Person
    label = "Attends an eligible educational institution for Lifetime Learning Credit"
    documentation = "Whether the person is enrolled at an eligible educational institution for Lifetime Learning Credit purposes."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#f_2"
