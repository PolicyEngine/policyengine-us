from policyengine_us.model_api import *


class ct_amt(Variable):
    value_type = float
    entity = Person
    label = "Connecticut alternative minimum tax (amt) rate"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(person, period, parameters):
        return [alternative_minimum_tax]
