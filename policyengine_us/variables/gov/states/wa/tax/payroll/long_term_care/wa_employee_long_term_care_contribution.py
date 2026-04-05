from policyengine_us.model_api import *


class wa_employee_long_term_care_contribution(Variable):
    value_type = float
    entity = Person
    label = "Washington employee long-term care contribution"
    documentation = "Employee-side Washington WA Cares Fund contribution."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.wa.tax.payroll.long_term_care.employee_rate
        return rate * person("payroll_tax_gross_wages", period)
