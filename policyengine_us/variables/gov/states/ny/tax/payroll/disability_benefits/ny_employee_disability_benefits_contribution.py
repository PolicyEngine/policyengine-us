from policyengine_us.model_api import *


class ny_employee_disability_benefits_contribution(Variable):
    value_type = float
    entity = Person
    label = "New York employee disability benefits contribution"
    documentation = (
        "Employee-side New York Disability Benefits withholding, annualized "
        "from the statutory weekly cap."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.tax.payroll.disability_benefits
        uncapped = p.employee_rate * person("payroll_tax_gross_wages", period)
        return min_(uncapped, p.annual_max_contribution)
