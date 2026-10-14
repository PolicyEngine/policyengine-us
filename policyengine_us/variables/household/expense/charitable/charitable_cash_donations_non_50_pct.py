from policyengine_us.model_api import *


class charitable_cash_donations_non_50_pct(Variable):
    value_type = float
    entity = Person
    label = "Charitable cash donations to non-50% limit organizations"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_B"

    def formula(person, period, parameters):
        cash_to_non_50 = person("charitable_cash_donations_non_50_pct_orgs", period)
        cash_50 = person("charitable_cash_donations_50_pct", period)
        cash_total = person("charitable_cash_donations", period)
        return where(
            cash_to_non_50 > 0,
            cash_to_non_50,
            max_(0, cash_total - cash_50),
        )
