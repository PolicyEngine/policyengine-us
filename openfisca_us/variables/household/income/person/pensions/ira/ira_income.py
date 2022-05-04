from openfisca_us.model_api import *


class ira_income(Variable):
    value_type = float
    entity = Person
    label = "IRA income"
    unit = USD
    documentation = "Income from all Individual Retirement Accounts."
    definition_period = YEAR

    formula = sum_of_variables(["tax_exempt_ira_income", "taxable_ira_income"])
