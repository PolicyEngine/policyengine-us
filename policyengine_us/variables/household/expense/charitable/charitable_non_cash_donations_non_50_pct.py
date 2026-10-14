from policyengine_us.model_api import *


class charitable_non_cash_donations_non_50_pct(Variable):
    value_type = float
    entity = Person
    label = "Charitable ordinary non-cash donations to non-50% limit organizations"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_B"

    def formula(person, period, parameters):
        ord_to_non_50 = person("charitable_non_cash_donations_non_50_pct_orgs", period)
        ord_50 = person("charitable_non_cash_donations_50_pct", period)
        ord_total = person("charitable_non_cash_donations", period)
        return where(
            ord_to_non_50 > 0,
            ord_to_non_50,
            max_(0, ord_total - ord_50),
        )
