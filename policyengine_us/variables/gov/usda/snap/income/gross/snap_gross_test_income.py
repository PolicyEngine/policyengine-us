from policyengine_us.model_api import *


class snap_gross_test_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP gross income for the gross income test"
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014#c",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_3_i",
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        # Certain states count the full income of certain ineligible aliens
        # under the gross income test while prorating it under the net
        # income test. This mirrors the composition of snap_gross_income
        # (snap_earned_income + snap_unearned_income
        # - snap_child_support_gross_income_deduction) with the full-count
        # share substituted for these aliens' income counted share.
        gross_income = spm_unit("snap_gross_income", period)
        person = spm_unit.members
        full_count = person("is_snap_gross_test_full_income_count_alien", period)
        share = person("snap_income_counted_share", period)
        gross_test_share = where(full_count, 1, share)
        employment = person("snap_earned_income_person", period)
        # Attribute unit-level net self-employment income by gross
        # self-employment income, as in snap_earned_income.
        countable = person("snap_countable_earner", period)
        gross_self_employment = person(
            "snap_gross_self_employment_income_person", period
        )
        unit_gross = spm_unit.sum(gross_self_employment)
        unit_net = spm_unit(
            "snap_self_employment_income_after_expense_deduction", period
        )
        counted_weight = spm_unit.sum(
            gross_self_employment * countable * gross_test_share
        )
        counted_self_employment = (
            unit_net * counted_weight / where(unit_gross > 0, unit_gross, 1)
        )
        earned = max_(
            spm_unit.sum(employment * gross_test_share) + counted_self_employment,
            0,
        )
        unearned = person("snap_unearned_income_person", period)
        p = parameters(period).gov.usda.snap.income
        unit_level_unearned = add(spm_unit, period, p.sources.unearned_spm_unit)
        # Count these aliens' child support payments in full as well, in
        # states that deduct child support when computing gross income.
        child_support = person("child_support_expense", period)
        state = spm_unit.household("state_code_str", period)
        cs_deductible = p.deductions.child_support[state]
        full_count_income = (
            earned
            + spm_unit.sum(unearned * gross_test_share)
            + unit_level_unearned
            - cs_deductible * spm_unit.sum(child_support * gross_test_share)
        )
        # Households without full-count aliens use snap_gross_income itself
        # so both tests read an identical income concept.
        return where(spm_unit.any(full_count), full_count_income, gross_income)
