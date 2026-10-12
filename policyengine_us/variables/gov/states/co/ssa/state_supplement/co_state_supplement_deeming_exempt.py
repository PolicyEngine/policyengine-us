from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class co_state_supplement_deeming_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Colorado State Supplement spouse or parent income not deemed"
    definition_period = MONTH
    # PDF page 95
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=95"

    def formula(person, period, parameters):
        # 9 CCR 2503-5 3.549(F): a spouse or parent who receives Adult
        # Financial grant payments, SSI or Medicaid "and has income no greater
        # than the SSI limit" has no income deemed to the AND-CS client.
        # SSA has found an SSI recipient's income within the SSI limit (for a
        # member of a couple, the couple's), so SSI receipt alone qualifies.
        # Each spouse of an SSI couple is then a client on their own income,
        # as 3.548(A) requires.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        p = parameters(period).gov.states.co.ssa.state_supplement.income.deeming
        if not p.assistance_exemption_applies:
            # Before March 2020, 3.545(F) excluded only the income from those
            # benefits, which the deemed income sources do not include.
            return receives_ssi
        # Old Age Pension is the Adult Financial program modeled for someone
        # who is not on SSI; AND-CS requires SSI.
        year = period.this_year
        adult_financial = person("co_oap", year) > 0
        medicaid = person("medicaid_enrolled_for_ssi_state_supplement", year)
        # The rule does not define the SSI limit. We read it as SSI's income
        # test for an individual: countable income, after SSI's exclusions,
        # no greater than the individual federal benefit rate.
        countable = _apply_ssi_exclusions(
            person("ssi_earned_income", year),
            person("ssi_unearned_income", year),
            parameters,
            year,
        )
        fbr = parameters(period).gov.ssa.ssi.amount.individual
        within_ssi_limit = countable <= fbr * MONTHS_IN_YEAR
        return receives_ssi | ((adult_financial | medicaid) & within_ssi_limit)
