from policyengine_us.model_api import *


class hourly_wage(Variable):
    value_type = float
    entity = Person
    label = "hourly wage"
    documentation = "Reported hourly wage, imputed from CPS ORG donors."
    unit = USD
    definition_period = YEAR
