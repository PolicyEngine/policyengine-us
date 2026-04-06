from policyengine_us.model_api import *


class il_hbwd_countable_unearned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities countable unearned income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.330",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
    )
    defined_for = StateCode.IL

    adds = "gov.states.il.hfs.hbwd.eligibility.income.sources.unearned"
