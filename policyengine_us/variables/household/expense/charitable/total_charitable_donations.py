from policyengine_us.model_api import *


class total_charitable_donations(Variable):
    value_type = float
    entity = Person
    label = "Total charitable donations"
    unit = USD
    definition_period = YEAR
    documentation = "Gross total charitable donations across all categories."
    reference = "https://www.law.cornell.edu/uscode/text/26/170"
    adds = [
        "resolved_charitable_cash_donations_50_pct",
        "resolved_charitable_cash_donations_non_50_pct",
        "resolved_charitable_non_cash_donations_50_pct",
        "resolved_charitable_non_cash_donations_non_50_pct",
        "resolved_charitable_capital_gain_donations_50_pct",
        "resolved_charitable_capital_gain_donations_non_50_pct",
    ]
