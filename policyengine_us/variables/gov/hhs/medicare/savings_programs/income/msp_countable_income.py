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
        # MSP uses SSI income methodology per 42 U.S.C. 1396d(p)(1)(B).
        # When both spouses are Medicare-eligible, SSI couple rules apply:
        # combine both incomes and apply the $20 exclusion once to the couple.
        is_medicare_eligible = person("is_medicare_eligible", period.this_year)
        both_medicare_eligible = person.marital_unit.sum(is_medicare_eligible) == 2

        earned = person("ssi_earned_income", period.this_year)
        unearned = person("ssi_unearned_income", period.this_year)

        # Aggregate couple income when both spouses are Medicare-eligible
        combined_earned = where(
            both_medicare_eligible,
            person.marital_unit.sum(earned),
            earned,
        )
        combined_unearned = where(
            both_medicare_eligible,
            person.marital_unit.sum(unearned),
            unearned,
        )

        # Apply SSI exclusions once to the (possibly combined) income
        annual_countable = _apply_ssi_exclusions(
            combined_earned, combined_unearned, parameters, period.this_year
        )
        return annual_countable / MONTHS_IN_YEAR
