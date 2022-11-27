from policyengine_us.model_api import *


class ctc_child_individual_maximum_arpa(Variable):
    value_type = float
    entity = Person
    label = "CTC maximum amount (child under ARPA)"
    unit = USD
    documentation = "The CTC entitlement in respect of this person as a child, under the American Rescue Plan Act."
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        amount = parameters(period).gov.irs.credits.ctc.amount.arpa.calc(age)
        return is_dependent * amount
