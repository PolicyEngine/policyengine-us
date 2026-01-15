from policyengine_us.model_api import *


class il_hbwd_countable_earned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities countable earned income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.360",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.362",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.370",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Per § 120.510(i), earned income exemptions apply only to the
        # disabled/blind worker's earnings, not to the spouse's.
        # Per § 120.510(f), the spouse's income is counted at gross.
        is_disabled = person("is_disabled", period)
        is_blind = person("is_blind", period)
        is_hbwd_worker = is_disabled | is_blind

        earned_income_with_exemption = person(
            "il_aabd_earned_income_after_exemption_person", period
        )
        gross_earned_income = person("il_hbwd_gross_earned_income", period)

        return where(
            is_hbwd_worker, earned_income_with_exemption, gross_earned_income
        )
