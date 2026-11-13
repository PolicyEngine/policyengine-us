from policyengine_us.model_api import *


class resolved_charitable_cash_donations_non_50_pct(Variable):
    value_type = float
    entity = Person
    label = "Resolved charitable cash donations to non-50% limit organizations"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_B"
    documentation = (
        "Resolved person-level charitable cash donations to non-50% limit organizations. "
        "When sub-box inputs are provided, they replace total donations. If both a total "
        "and both sub-boxes are set with the total larger, the sub-box inputs take precedence "
        "and any excess on the total is dropped."
    )

    def formula(person, period, parameters):
        cash_to_non_50 = person("charitable_cash_donations_non_50_pct_orgs", period)
        cash_50_explicit = person("charitable_cash_donations_50_pct_orgs", period)
        cash_total = person("charitable_cash_donations", period)
        residual = where(
            cash_50_explicit > 0,
            max_(0, cash_total - cash_50_explicit),
            0,
        )
        return where(
            cash_to_non_50 > 0,
            cash_to_non_50,
            residual,
        )
