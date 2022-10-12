from policyengine_us.model_api import *


class local_sales_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local sales tax"
    unit = USD
