from policyengine_us.model_api import *


class assessed_property_value(Variable):
    value_type = float
    entity = Person
    label = "Assessed property value"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR

    def formula(person, period, parameters):
        state_code = person.household("state_code_str", period)
        assessment_rate = parameters(period).gov.local.tax.assessment_rate[state_code]
        return person("primary_residence_value", period) * assessment_rate
