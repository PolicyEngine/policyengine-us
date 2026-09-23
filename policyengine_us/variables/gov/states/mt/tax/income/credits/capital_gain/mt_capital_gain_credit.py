from policyengine_us.model_api import *


class mt_capital_gain_credit(Variable):
    value_type = float
    entity = Person
    label = "Montana capital gain credit"
    unit = USD
    definition_period = YEAR
    reference = "https://rules.mt.gov/gateway/RuleNo.asp?RN=42%2E4%2E502"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.credits.capital_gain

        # The credit is 2% of net capital gains (Form 2 instructions, Line 1),
        # so a net capital loss produces no credit rather than a negative one.
        net_capital_gain = max_(person("capital_gains", period), 0)
        return p.percentage * net_capital_gain
