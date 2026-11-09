from policyengine_us.model_api import *


class sc_tanf_child_support_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF child support paid deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        "https://www.scstatehouse.gov/coderegs/Chapter%20114.pdf#page=212",
        # PDF pages 131, 134
        "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=131",
    )
    documentation = (
        "Child support that benefit group members pay to legal dependents "
        "outside the group, taken from each payer's own income after the "
        "earned income disregards. It never takes a payer's income below zero."
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # 114-1140(L): support that a budget group member pays to legal
        # dependents outside the group "may be deducted from the income of
        # the payor". The yearly input is read monthly, as
        # sc_tanf_gross_unearned_income reads its sources.
        support_paid = max_(person("child_support_expense", period), 0)
        # The payer's income is earned income after the Section 8.12
        # disregards (Section 8.16 C and D), then unearned income (8.16 F).
        # Neither variable counts an SSI recipient's income, and the earned
        # one leaves out a dependent child's earnings, so that income can't
        # absorb a deduction.
        own_income = add(
            person,
            period,
            [
                "sc_tanf_countable_earned_income_person",
                "sc_tanf_gross_unearned_income",
            ],
        )
        return spm_unit.sum(min_(support_paid, max_(own_income, 0)))
