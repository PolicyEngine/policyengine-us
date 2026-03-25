from policyengine_us.model_api import *


class employer_total_medicare_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer total Medicare payroll tax"
    documentation = (
        "Employer-level Medicare payroll tax liability from aggregate payroll "
        "wages inputs."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.payroll.medicare.rate
        gross_wages = person("employer_total_payroll_tax_gross_wages", period)
        return p.employer * gross_wages
