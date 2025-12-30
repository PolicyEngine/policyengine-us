from policyengine_us.model_api import *


class il_hbi_senior_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Illinois HBIS countable income using AABD methodology"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=161600",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.120",
    )
    # Per Illinois DHS, HBIS follows AABD community eligibility criteria
    # for income counting. This variable reuses the AABD income methodology
    # without the AABD-specific eligibility restrictions.

    adds = [
        "il_aabd_earned_income_after_exemption_person",
        "il_aabd_countable_unearned_income",
    ]
