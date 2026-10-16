from policyengine_us.model_api import *


class in_claim_of_right_repayment_excluded_from_income(Variable):
    value_type = float
    entity = Person
    label = "Claim of right repayment not included in Indiana income when received"
    unit = USD
    documentation = (
        "Part of claim_of_right_repayment that was not included in Indiana "
        "adjusted gross income in the earlier year it was received, such as "
        "repaid Social Security benefits, or the extra Indiana unemployment "
        "compensation deduction the earlier return would have had without the "
        "repaid amount. Indiana's repayment deduction excludes it."
    )
    definition_period = YEAR
    reference = (
        # IC 6-3-1-3.5(a)(22)
        "https://www.in.gov/sba/files/HB1001-Final.pdf#page=117",
        # 2025 IT-40 instructions, deduction 630, unemployment compensation note
        "https://forms.in.gov/Download.aspx?id=16915#page=23",
    )
    defined_for = StateCode.IN
