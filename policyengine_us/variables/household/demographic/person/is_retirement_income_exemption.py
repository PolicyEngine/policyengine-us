from policyengine_us.model_api import *


class is_no_retirement_income_exemption(Variable):
    value_type = bool
    entity = Person
    label = "Is a taxpayer not claiming a retirement income exemption"
    definition_period = YEAR
