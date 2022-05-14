from openfisca_us.model_api import *


class state_sales_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "State sales tax"
    unit = USD
    definition_period = YEAR
