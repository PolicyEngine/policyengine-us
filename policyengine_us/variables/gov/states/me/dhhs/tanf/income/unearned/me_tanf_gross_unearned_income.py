from policyengine_us.model_api import *


class me_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Maine Temporary Assistance for Needy Families (TANF) gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.law.cornell.edu/regulations/maine/C-M-R-10-144-ch-331-III",
    )
    defined_for = StateCode.ME

    adds = "gov.states.me.dhhs.tanf.income.sources.unearned"
