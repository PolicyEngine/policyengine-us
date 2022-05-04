from openfisca_us.model_api import *


class tax_exempt_ira_income(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt IRA income."
    unit = USD
    documentation = "Income from Roth IRAs."
    definition_period = YEAR
