from openfisca_us.model_api import *


class taxable_ira_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable IRA income."
    unit = USD
    documentation = "Income from traditional IRAs."
    definition_period = YEAR
