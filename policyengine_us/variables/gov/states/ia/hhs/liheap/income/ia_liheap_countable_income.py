from policyengine_us.model_api import *


class ia_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Iowa LIHEAP countable income"
    documentation = (
        "Annual gross countable income of all household members aged 18 and "
        "over, including members excluded from household size, less child "
        "support paid by a household member, floored at zero. Annual model "
        "amounts stand in for the 30-day, 12-month or calendar-year "
        "verification period the household elects under Section 6.10."
    )
    reference = (
        # Sections 6.10, 6.20 and 7.30, and Appendix C Child Support notes.
        # PDF pages 24, 26, 34, 92-93
        "https://hhs.iowa.gov/media/17262/download?inline#page=24",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        gross = add(
            spm_unit,
            period,
            [
                "ia_liheap_countable_earned_income",
                "ia_liheap_countable_unearned_income",
            ],
        )
        # Appendix C, Child Support: "For the party paying child support, a
        # payment record is required as proof of payment in order for it to be
        # deducted from countable income". Child support received is not
        # counted and is not in the income source lists.
        child_support_paid = add(spm_unit, period, ["child_support_expense"])
        return max_(gross - child_support_paid, 0)
