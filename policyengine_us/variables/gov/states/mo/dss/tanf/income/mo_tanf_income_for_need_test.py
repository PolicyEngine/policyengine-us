from policyengine_us.model_api import *


class mo_tanf_income_for_need_test(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF income for Standard of Need test"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-10/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30-20/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf.earned_income_disregard
        # 13 CSR 40-2.310(11): the Standard of Need test counts total
        # income "without application of the earned income disregards
        # provided for in paragraphs (9)(A)2.-5." — no work expense,
        # $30 plus one-third, $30-only, or dependent care deduction.
        # The student-child and teen-parent exemptions of (9)(A)1. and
        # 6. are not suspended; they are already excluded from
        # mo_tanf_gross_earned_income. The (9)(C)1. six-month calendar
        # limit on the student exemption and the (9)(C)2. pass-through
        # of the $30 plus one-third disregard for persons who received
        # TA in one of the four preceding months require month-level
        # history and are not modeled.
        gross_earned = spm_unit("mo_tanf_gross_earned_income", period)
        gross_unearned = spm_unit("mo_tanf_gross_unearned_income", period)
        # The (9)(D) two-thirds disregard is not among the suspended
        # paragraphs, so an active participant's earnings count at
        # one-third in the need test (DSS Manual 0210.015.30.20:
        # "eligibility and grant amount are determined using the
        # two-thirds disregard").
        two_thirds = gross_earned * p.two_thirds_disregard.percentage
        is_enrolled = spm_unit("is_tanf_enrolled", period)
        counted_earned = where(is_enrolled, gross_earned - two_thirds, gross_earned)
        return counted_earned + gross_unearned
