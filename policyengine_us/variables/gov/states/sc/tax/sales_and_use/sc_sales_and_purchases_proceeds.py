from policyengine_us.model_api import *


class sc_sales_and_purchases_proceeds(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina sales and purchases proceeds"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
