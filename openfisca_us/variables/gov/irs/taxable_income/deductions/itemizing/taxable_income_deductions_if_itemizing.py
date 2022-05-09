from openfisca_us.model_api import *


class taxable_income_deductions_if_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable income deductions if itemizing"
    unit = USD
    definition_period = YEAR

