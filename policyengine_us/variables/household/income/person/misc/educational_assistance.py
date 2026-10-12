from policyengine_us.model_api import *


class educational_assistance(Variable):
    value_type = float
    entity = Person
    label = "educational assistance"
    documentation = "Scholarships, grants, and other educational assistance."
    unit = USD
    definition_period = YEAR
