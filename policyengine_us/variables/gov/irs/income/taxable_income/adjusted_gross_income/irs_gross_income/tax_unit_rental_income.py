from policyengine_us.model_api import *


class tax_unit_rental_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit rental income"
    unit = USD
    documentation = "Combined rental income for the tax unit."
    definition_period = YEAR

    adds = ["rental_income"]
