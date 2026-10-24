from policyengine_us.model_api import *


class az_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Arizona LIHEAP countable income"
    documentation = (
        "Annual gross household income counted under Arizona LIHEAP, including "
        "the income of members who are not citizens or qualified noncitizens. "
        "Annual amounts stand for twelve times the policy's 30-day income "
        "snapshot."
    )
    unit = USD
    reference = (
        # PDF pages 4, 8-9, 14, 32
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=4",
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2026/state-plans/AZ_Plan_2026.pdf#page=5",
    )
    defined_for = StateCode.AZ

    # Section VII.A.1.c.v annualizes the 30-day snapshot as "([Average Gross
    # Income per Pay Period X Income Frequency] / 12)", so annual income over
    # twelve is the policy's own arithmetic. Cash Assistance is a household
    # benefit with no person-level attribution, so it is summed here rather
    # than in the person-level unearned source list: Section VI.A.6.e.ii.B
    # counts "Social Security and TANF benefits", and Section VII.B.1.c.ii adds
    # "the Cash Assistance benefit" to the reported income of households
    # categorically eligible through it. The take-up-gated tanf includes
    # Arizona Cash Assistance, so a family that does not take it up has none
    # counted. The policy's narrower base for categorically eligible
    # households (the enrolled member's reported income) is not modeled; the
    # whole household's countable income is used.
    adds = [
        "az_liheap_countable_earned_income",
        "az_liheap_countable_unearned_income",
        "tanf",
    ]
