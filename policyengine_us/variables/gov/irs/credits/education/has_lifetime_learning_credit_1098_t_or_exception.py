from policyengine_us.model_api import *


class has_lifetime_learning_credit_1098_t_or_exception(Variable):
    value_type = bool
    entity = Person
    label = "Has Form 1098-T or an LLC exception"
    documentation = "Whether the student received Form 1098-T or meets an exception allowing the Lifetime Learning Credit to be claimed with substantiated qualified expenses."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#g_8"
