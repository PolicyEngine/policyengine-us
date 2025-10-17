from policyengine_us.model_api import *


class is_citizen_or_legal_immigrant(Variable):
    value_type = bool
    entity = Person
    label = "Is citizen or qualified noncitizen under federal law"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/8/1641"
