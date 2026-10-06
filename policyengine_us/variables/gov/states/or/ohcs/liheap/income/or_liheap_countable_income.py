from policyengine_us.model_api import *


class or_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Oregon LIHEAP countable household income"
    unit = USD
    defined_for = StateCode.OR
    # PDF pages 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
    # 51, 52, 53, 54, 55, 56.
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=35"
    documentation = (
        "Annual income approximates the allowed one-, three- or twelve-month "
        "observation window. Interest is assumed withdrawn, and the $200 test is "
        "applied to each member's interest, a reading the manual does not specify. "
        "Each unearned source is floored at zero like the earned sources, so a rental "
        "or estate loss does not offset other income. Enter disability_benefits as the "
        "private insurer's payment after any Social Security offset; Social Security "
        "is counted separately, reproducing the manual's examples without deducting "
        "the offset twice. Unsupported details include regular gifts, foster and "
        "adoption payments, tribal receipts, work-study and caregiver payments within "
        "the household. Military wages should be included in employment_income. Use a "
        "direct countable-income override when these details matter."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].ohcs.liheap.income
        person = spm_unit.members
        interest = person("interest_income", period)
        counted_interest = spm_unit.sum(
            where(interest > p.interest_threshold, interest, 0)
        )
        # The TANF source counts receipt after take-up, not or_tanf entitlement.
        # Landlords complete the self-employment form (page 35), so a loss in one
        # source cannot offset another, as in the earned-income formula.
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(add(spm_unit, period, [source]), 0)
        return (
            add(spm_unit, period, ["or_liheap_countable_earned_income"])
            + unearned
            + counted_interest
        )
