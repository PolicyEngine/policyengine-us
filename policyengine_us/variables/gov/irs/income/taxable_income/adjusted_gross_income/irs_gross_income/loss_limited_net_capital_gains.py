from policyengine_us.model_api import *


class loss_limited_net_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Loss-limited net capital gains"
    unit = USD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        filing_status = tax_unit("filing_status", period)
        loss_limit = p.capital_gains.loss_limit[filing_status]
        net_capital_gains = tax_unit("net_capital_gains", period)
        return max_(-loss_limit, net_capital_gains)
