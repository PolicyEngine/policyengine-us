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

    adds = ["il_aabd_earned_income_after_exemption_person"]
    # HBWD uses the same earned income calculation as AABD per
    # 89 Ill. Admin. Code § 120.510(i) referencing § 120.362 and § 120.370
    # § 120.362 and § 113.120 have identical exemption amounts:
    # - $25 flat exemption (§ 120.362(a) / § 113.120(a))
    # - $20 + 50% of next $60 for disabled workers (§ 120.362(b)(1) / § 113.120(b))
    # § 120.370 references AABD MANG work expense deductions
