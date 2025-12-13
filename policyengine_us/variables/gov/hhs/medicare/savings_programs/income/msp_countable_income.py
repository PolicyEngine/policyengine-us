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
    """

    def formula(person, period, parameters):
        # MSP uses SSI income methodology per 42 U.S.C. 1396d(p)(1)(B)
        earned = person("ssi_earned_income", period.this_year)
        unearned = person("ssi_unearned_income", period.this_year)
        # Apply SSI exclusions ($20 general, $65 earned, 50% remaining)
        annual_countable = _apply_ssi_exclusions(
            earned, unearned, parameters, period.this_year
        )
        return annual_countable / MONTHS_IN_YEAR
