from openfisca_us.model_api import *


class payroll_tax_gross_wages(Variable):
    value_type = float
    entity = Person
    label = "Gross wages and salaries for payroll taxes"
    definition_period = YEAR
    unit = USD

    formula = sum_of_variables(["employment_income", "pension_contributions"])
