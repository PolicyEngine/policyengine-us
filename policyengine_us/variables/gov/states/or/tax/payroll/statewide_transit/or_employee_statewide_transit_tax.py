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
        rate = (
            parameters(period)
            .gov.states["or"]
            .tax.payroll.statewide_transit.employee_rate
        )
        return rate * person("payroll_tax_gross_wages", period)
