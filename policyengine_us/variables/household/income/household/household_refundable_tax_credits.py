from policyengine_us.model_api import *


class household_refundable_tax_credits(Variable):
    value_type = float
    entity = Household
    label = "refundable tax credits"
    definition_period = YEAR
    unit = USD
    adds = [
        "income_tax_refundable_credits_in_force",
        # The premium tax credit is a refundable credit (26 U.S.C. 36B), but
        # mostly paid in advance to the insurer, with the return reconciling
        # the difference. It counts here rather than in income_tax, which
        # stays what the return shows and what SPM resources net.
        "premium_tax_credit_in_force",
        "household_refundable_state_tax_credits",
        "household_refundable_local_tax_credits",
    ]
