from policyengine_us.model_api import *


class partnership_s_corp_income_would_be_qualified(Variable):
    value_type = bool
    entity = Person
    label = "Partnership and S-corp income would be qualified"
    documentation = "Whether income from partnerships and S corporations would be considered qualified business income."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#c_3_A"
    default_value = True
