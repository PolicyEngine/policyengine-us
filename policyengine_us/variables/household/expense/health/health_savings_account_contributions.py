from policyengine_us.model_api import *


class health_savings_account_payroll_contributions(Variable):
    value_type = float
    entity = Person
    # Separate from health_savings_account_ald which are not made through
    # payroll deductions.
    label = "Health Savings Account payroll contributions"
    unit = USD
    definition_period = YEAR
    # Contributions are capped by 26 U.S.C. 223(b)(2), which 223(g) indexes
    # to chained CPI-U. Following the family limit keeps an amount at the cap
    # at the cap in later years; the family amount's $50 rounding is the
    # smaller share, so its growth is closest to the 223(g) adjustment.
    uprating = "gov.irs.gross_income.health_savings_account_contributions.limit.family"
