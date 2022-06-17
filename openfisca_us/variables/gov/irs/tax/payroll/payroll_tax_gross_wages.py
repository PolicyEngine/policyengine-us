from openfisca_us.model_api import *


class payroll_tax_gross_wages(Variable):
    value_type = float
    entity = Person
    label = "Gross wages and salaries for payroll taxes"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        earnings = person("employment_income", period)
        pension_contributions = person("pension_contributions", period)
        return max_(0, earnings - pension_contributions)

