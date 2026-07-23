from policyengine_us.model_api import *


class ut_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Utah CCAP countable income"
    definition_period = MONTH
    defined_for = StateCode.UT
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-710"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.ccap.income
        gross_income = spm_unit("ut_ccap_gross_income", period)
        person = spm_unit.members
        # The CC client is a parent, specified relative, or court-appointed
        # guardian (R986-700-702(2)): is_parent identifies parent clients,
        # and when no parent lives in the household the tax-unit head or
        # spouse proxies the nonparent caretaker client, mirroring
        # ut_ccap_gross_income.
        is_parent = person("is_parent", period.this_year)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        no_parent_present = spm_unit.sum(is_parent) == 0
        is_client = is_parent | (
            spm_unit.project(no_parent_present) & is_head_or_spouse
        )
        earned_income = add(person, period, p.sources.earned)
        # The first $50 of child support received by the family is deducted
        # (R986-700-710(5)(a)).
        child_support_received = add(spm_unit, period, ["child_support_received"])
        child_support_deduction = min_(
            child_support_received,
            p.deductions.child_support_received_deduction,
        )
        # Court-ordered child support and alimony paid out by the household
        # are deducted (R986-700-710(5)(b)).
        support_paid = add(
            spm_unit, period, ["child_support_expense", "alimony_expense"]
        )
        # $100 is deducted for each person with countable earned income
        # (R986-700-710(5)(c)); only the client's earned income is
        # countable (R986-700-710(4)(a) and (4)(f)), so only client
        # earners generate the deduction.
        counted_earners = spm_unit.sum((earned_income > 0) & is_client)
        earned_income_deduction = p.deductions.earned_income_deduction * counted_earners
        # A $100 automatic medical deduction applies without proof of
        # expenditure (R986-700-710(5)(d)).
        deductions = (
            child_support_deduction
            + support_paid
            + earned_income_deduction
            + p.deductions.medical_deduction
        )
        return max_(gross_income - deductions, 0)
