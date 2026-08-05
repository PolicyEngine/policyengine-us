from policyengine_us.model_api import *


class assessed_property_value(Variable):
    value_type = float
    entity = Person
    label = "Assessed property value"
    documentation = (
        "Total assessed value of property owned by this person, derived by "
        "applying the state assessment rate to the person's primary residence "
        "value. In microsimulation neither assessed_property_value nor "
        "primary_residence_value is populated in the microdata, so this "
        "variable is 0 unless a user enters a value. primary_residence_value "
        "is a Person-level input capturing each person's share of the "
        "residence; this variable is also Person-level and multiplies that "
        "input by a state-level assessment rate, so ownership shares held by "
        "different household members are assessed independently rather than "
        "aggregated to the household."
    )
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR

    def formula(person, period, parameters):
        state_code = person.household("state_code_str", period)
        assessment_rate = parameters(period).gov.local.tax.assessment_rate[state_code]
        return person("primary_residence_value", period) * assessment_rate
