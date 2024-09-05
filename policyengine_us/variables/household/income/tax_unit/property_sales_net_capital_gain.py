from policyengine_us.model_api import *


class property_sales_net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net capital gains from sale or exchange of property"
    unit = USD
    definition_period = YEAR
