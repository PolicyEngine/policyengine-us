from policyengine_us.model_api import *


class az_aged_exemption(Variable):
    value_type = float
    entity = Person
    label = "Arizona aged exemption"
    unit = USD
    definition_period = YEAR
    defined_for = "az_aged_exemption_eligible_person"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.az.tax.income.exemptions

        age = person("age", period)
        return p.aged.calc(age)
