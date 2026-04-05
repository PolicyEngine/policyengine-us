from policyengine_us.model_api import *


class ca_employee_state_disability_insurance_contribution(Variable):
    value_type = float
    entity = Person
    label = "California employee state disability insurance contribution"
    documentation = (
        "Employee-side California State Disability Insurance withholding, "
        "which funds SDI and Paid Family Leave."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.ca.tax.payroll.disability.employee_rate
        return rate * person("payroll_tax_gross_wages", period)
