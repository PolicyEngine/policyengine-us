from policyengine_us.model_api import *


class yearly_pregnancy_months(Variable):
    value_type = int
    entity = Person
    label = "The number of months a person is pregnant in a year"
    definition_period = YEAR
