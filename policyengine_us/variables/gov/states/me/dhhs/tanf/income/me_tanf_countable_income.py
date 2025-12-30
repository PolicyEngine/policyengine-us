from policyengine_us.model_api import *


class me_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331",
    )
    defined_for = StateCode.ME

    adds = [
        "me_tanf_countable_earned_income",
        "me_tanf_countable_unearned_income",
    ]
