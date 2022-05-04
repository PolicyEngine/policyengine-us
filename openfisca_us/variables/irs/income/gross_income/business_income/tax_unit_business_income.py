from openfisca_us.model_api import *


class tax_unit_business_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Business income (losses ignored)"
    unit = USD
    documentation = "Business income, capped at zero."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        profit = tax_unit("tax_unit_self_employment_income", period)
        rents = tax_unit("tax_unit_rental_income", period)
        positive_profit = max_(profit, 0)
        positive_rents = max_(rents, 0)
        return positive_profit + positive_rents