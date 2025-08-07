from policyengine_us.model_api import *


class tax_preparation_fees(Variable):
    value_type = float
    entity = Person
    label = "Tax preparation fees"
    unit = USD
    definition_period = YEAR
