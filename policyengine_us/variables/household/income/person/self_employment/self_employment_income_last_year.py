from policyengine_us.model_api import *


class self_employment_income_last_year(Variable):
    value_type = float
    entity = Person
    label = "Label"
    unit = USD
    documentation = "Description"
    definition_period = YEAR


class previous_year_income_imputed(Variable):
    value_type = bool
    entity = Person
    label = "Label"
    unit = USD
    documentation = "Description"
    definition_period = YEAR
