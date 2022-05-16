from openfisca_us.model_api import *


class medicaid_income_level(Variable):
    value_type = float
    entity = Person
    label = "Medicaid income level"
    unit = "/1"
    documentation = "Income for Medicaid as a percentage of the federal poverty line for this person."
    definition_period = YEAR

    def formula(person, period, parameters):
        income = person.tax_unit("medicaid_income", period)
        fpg = person.tax_unit("tax_unit_fpg", period)
        return income / fpg
