from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class msp_countable_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program countable monthly income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396d#p",
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501715010",
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
    )
    documentation = """
    MSP countable income uses SSI methodology per 42 U.S.C. 1396d(p)(1)(B),
    which specifies income "determined under section 1382a" (SSI rules).
    This applies the standard SSI exclusions:
    1. $20 general income exclusion (from unearned first)
    2. $65 earned income exclusion
    3. 50% of remaining earned income excluded

    For married couples where both spouses are Medicare-eligible, SSI couple
    rules apply per 20 CFR 416.1160: both spouses' incomes are combined before
    exclusions are applied, and the $20 exclusion is taken once on the combined
    income. The combined countable income is then compared against the couple FPL
    in the eligibility variables (is_qmb_eligible, is_slmb_eligible, is_qi_eligible).
    """

    def formula(person, period, parameters):
        earned_income = person("ssi_earned_income", period)
        unearned_income = person("ssi_unearned_income", period)
        is_medicare_eligible = person("is_medicare_eligible", period)
        both_medicare_eligible = person.marital_unit.sum(is_medicare_eligible) == 2

        blind_or_disabled_working_student_exclusion = person(
            "ssi_blind_or_disabled_working_student_exclusion", period
        )
        personal_earned_income = max_(
            earned_income - blind_or_disabled_working_student_exclusion,
            0,
        )
        deeming_applies = person("is_ssi_spousal_deeming_applies_monthly", period)

        spouse_earned_income = person(
            "ssi_earned_income_deemed_from_ineligible_spouse_monthly", period
        )
        spouse_unearned_income = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse_monthly", period
        )
        personal_countable_income = _apply_ssi_exclusions(
            personal_earned_income,
            unearned_income,
            parameters,
            period,
            monthly=True,
        )

        couple_countable = _apply_ssi_exclusions(
            max_(
                person.marital_unit.sum(earned_income)
                - person.marital_unit.sum(blind_or_disabled_working_student_exclusion),
                0,
            ),
            person.marital_unit.sum(unearned_income),
            parameters,
            period,
            monthly=True,
        )

        deemed_countable = _apply_ssi_exclusions(
            personal_earned_income + spouse_earned_income,
            unearned_income + spouse_unearned_income,
            parameters,
            period,
            monthly=True,
        )

        single_countable = where(
            deeming_applies, deemed_countable, personal_countable_income
        )

        return where(both_medicare_eligible, couple_countable, single_countable)
