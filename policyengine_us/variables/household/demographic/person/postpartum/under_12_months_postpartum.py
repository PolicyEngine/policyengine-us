from policyengine_us.model_api import *


class under_12_months_postpartum(Variable):
    value_type = bool
    entity = Person
    label = "Under 12 months postpartum"
    definition_period = YEAR
