from policyengine_us.model_api import *


class net_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Net capital gains before loss limitation"
    unit = USD
    adds = ["long_term_capital_gains", "short_term_capital_gains"]
