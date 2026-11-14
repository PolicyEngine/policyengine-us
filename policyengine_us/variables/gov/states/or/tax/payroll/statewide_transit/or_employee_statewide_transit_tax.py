from policyengine_us.model_api import *


class or_employee_statewide_transit_tax(Variable):
    value_type = float
    entity = Person
    label = "Oregon employee statewide transit tax"
    documentation = "Employee-side Oregon statewide transit tax withholding."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.OR

    def formula(person, period, parameters):
        rate = person("or_employee_statewide_transit_tax_rate", period)
        return rate * person("or_statewide_transit_taxable_wages", period)
