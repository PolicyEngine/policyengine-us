from policyengine_us.model_api import *


class sc_tanf_child_support_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF child support paid deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        # PDF pages 131, 134
        "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=131",
    )
    documentation = (
        "Child support that benefit group members who are not dependent "
        "children pay outside the home, deducted after the earned income "
        "disregards from earned income first and then from unearned income, "
        "never below zero."
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # Section 7.7 leaves SSI recipients out of the benefit group, and
        # dependent children's earnings are excluded (Section 7.5), so only
        # the other members' support counts. The yearly input is read
        # monthly, as sc_tanf_gross_unearned_income reads its sources.
        payer = ~person("sc_tanf_ssi_recipient", period) & ~person(
            "sc_tanf_dependent_child", period
        )
        support_paid = spm_unit.sum(
            max_(person("child_support_expense", period), 0) * payer
        )
        # Sections 8.11 and 8.16 D and F deduct it from the group's earned
        # income after the Section 8.12 disregards, then from unearned
        # income. A group with no income gets no deduction (Section 8.11(2)).
        earned = add(spm_unit, period, ["sc_tanf_countable_earned_income_person"])
        unearned = add(spm_unit, period, ["sc_tanf_gross_unearned_income"])
        return min_(support_paid, max_(earned + unearned, 0))
