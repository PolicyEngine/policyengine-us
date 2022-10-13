from openfisca_us.model_api import *


class or_income_after_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR income after subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        income_after_additions = tax_unit("or_income_after_additions", period)
        subtractions = tax_unit("or_income_subtractions", period)
        return income_after_additions - subtractions
