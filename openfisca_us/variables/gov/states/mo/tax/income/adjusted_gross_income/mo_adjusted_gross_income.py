from openfisca_us.model_api import *


class mo_adjusted_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "",
        "",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        gross_income = person("irs_gross_income", period)
        subtractions = person("mo_qualified_health_insurance_premiums", period)
        return gross_income - subtractions
