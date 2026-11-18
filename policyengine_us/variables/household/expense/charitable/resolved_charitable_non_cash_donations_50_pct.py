from policyengine_us.model_api import *


class resolved_charitable_non_cash_donations_50_pct(Variable):
    value_type = float
    entity = Person
    label = "Resolved charitable non-cash donations to 50% limit organizations"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_A"
    documentation = (
        "Resolved person-level ordinary non-cash charitable donations to 50% limit organizations. "
        "When sub-box inputs are provided, they replace total donations. If both a total "
        "and both sub-boxes are set with the total larger, the sub-box inputs take precedence "
        "and any excess on the total is dropped."
    )

    def formula(person, period, parameters):
        ord_50_explicit = person("charitable_non_cash_donations_50_pct_orgs", period)
        ord_to_non_50 = person("charitable_non_cash_donations_non_50_pct_orgs", period)
        ord_total = person("charitable_non_cash_donations", period)
        return where(
            ord_50_explicit > 0,
            ord_50_explicit,
            max_(0, ord_total - ord_to_non_50),
        )
