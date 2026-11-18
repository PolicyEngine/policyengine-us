from policyengine_us.model_api import *


class nc_claim_of_right_repayment_excluded_from_income(Variable):
    value_type = float
    entity = Person
    label = "Claim of right repayment excluded from North Carolina income when received"
    unit = USD
    documentation = (
        "Part of claim_of_right_repayment that North Carolina deducted from "
        "adjusted gross income in the earlier year it was received, such as "
        "repaid Social Security benefits or Bailey-exempt retirement benefits."
    )
    definition_period = YEAR
    reference = (
        # N.C. Gen. Stat. 105-153.5(a)(2)d as rewritten by S.L. 2026-31,
        # section 1.8, PDF pages 5-6
        "https://www.ncleg.gov/EnactedLegislation/SessionLaws/PDF/2025-2026/SL2026-31.pdf#page=5",
    )
    defined_for = StateCode.NC
