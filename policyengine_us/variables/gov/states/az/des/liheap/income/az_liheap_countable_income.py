from policyengine_us.model_api import *


class az_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Arizona LIHEAP countable income"
    documentation = (
        "Annual gross household income counted under Arizona LIHEAP, including "
        "the income of members who are not citizens or qualified noncitizens, "
        "less each member's out-of-pocket Medicare Part B premium and floored "
        "at zero. Policy VII.A.1.c.ii.D (CCSD-LIHEAP-Policy.pdf#page=14): "
        "'Expenses related to Medicare (such as premiums) should be subtracted "
        "when determining gross income'; Part D has no premium variable and is "
        "not deducted. Annual amounts stand for twelve times the policy's "
        "30-day income snapshot."
    )
    unit = USD
    reference = (
        # PDF pages 4, 8-9, 14, 32
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=4",
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2026/state-plans/AZ_Plan_2026.pdf#page=5",
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # Section VII.A.1.c.v annualizes the 30-day snapshot as "([Average
        # Gross Income per Pay Period X Income Frequency] / 12)", so annual
        # income over twelve is the policy's own arithmetic. Cash Assistance
        # is a household benefit with no person-level attribution, so it is
        # summed here rather than in the person-level unearned source list:
        # Section VI.A.6.e.ii.B counts "Social Security and TANF benefits", and
        # Section VII.B.1.c.ii adds "the Cash Assistance benefit" to the
        # reported income of households categorically eligible through it. The
        # take-up-gated tanf includes Arizona Cash Assistance, so a family that
        # does not take it up has none counted. The policy's narrower base for
        # categorically eligible households (the enrolled member's reported
        # income) is not modeled; the whole household's countable income is
        # used.
        gross_income = add(
            spm_unit,
            period,
            [
                "az_liheap_countable_earned_income",
                "az_liheap_countable_unearned_income",
                "tanf",
            ],
        )
        # Section VII.A.1.c.ii.D note (CCSD-LIHEAP-Policy.pdf#page=14):
        # "Expenses related to Medicare (such as premiums) should be
        # subtracted when determining gross income." Plan Section 1.9 counts
        # SSA benefits "Excluding MediCare deduction". medicare_part_b_premium
        # is each member's out-of-pocket Part B premium, zero for a member who
        # is not enrolled or whose premium a Medicare Savings Program pays; no
        # Part D premium variable exists.
        medicare_premiums = add(spm_unit, period, ["medicare_part_b_premium"])
        return max_(gross_income - medicare_premiums, 0)
