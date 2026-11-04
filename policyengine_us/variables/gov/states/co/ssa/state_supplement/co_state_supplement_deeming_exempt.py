from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.states.co.ssa.oap._precision import (
    PRECISION,
    ssi_paid,
)


class co_state_supplement_deeming_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Colorado State Supplement spouse or parent income not deemed"
    definition_period = MONTH
    # Not restricted to Colorado: 3.549(F) sets no residence condition on the
    # spouse or parent.
    # PDF page 95
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=95"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.ssa.state_supplement.income.deeming
        if not p.assistance_exemption_applies:
            # Before March 2020, 3.545(F) excluded only "the income from those
            # benefits" (public assistance, SSI or medical assistance), which
            # the deemed income sources do not include. The recipient's other
            # income was deemed.
            return np.zeros(person.count, dtype=bool)
        # 9 CCR 2503-5 3.549(F): a spouse or parent who receives Adult
        # Financial grant payments, SSI or Medicaid "and has income no
        # greater than the SSI limit" has no income deemed to the AND-CS
        # client. The rule doesn't define the SSI limit. We read it as the
        # limit SSI applies to the person, as 3.570.43 uses the phrase:
        # someone who receives SSI meets it, since SSI's own test held
        # their countable income within it (the couple rate in an eligible
        # couple). Someone on Old Age Pension or Medicaid without SSI meets
        # it when their own monthly countable income, after SSI's
        # exclusions, doesn't exceed the individual federal benefit rate.
        countable = _apply_ssi_exclusions(
            person("ssi_earned_income", period) * MONTHS_IN_YEAR,
            person("ssi_unearned_income", period) * MONTHS_IN_YEAR,
            parameters,
            period,
        )
        fbr = parameters(period).gov.ssa.ssi.amount.individual
        within_limit = countable <= (fbr + PRECISION) * MONTHS_IN_YEAR
        ssi = ssi_paid(person("ssi", period))
        receives_ssi = (ssi > 0) | person("receives_ssi", period)
        # Old Age Pension is the Adult Financial program modeled for someone
        # who is not on SSI; AND-CS requires SSI. Receipt is judged month by
        # month on the person's own income, as co_oap_deeming_exempt judges
        # it.
        p_oap = parameters(period).gov.states.co.ssa.oap
        oap_income = person("co_oap_own_countable_income", period) + ssi
        receives_oap = person("co_oap_eligible", period.this_year) & (
            p_oap.grant_standard - oap_income > PRECISION
        )
        exempt = receives_ssi | (within_limit & receives_oap)
        # Medicaid decides only for someone within the limit, not exempt
        # otherwise, who shares a marital unit, tax unit or household with
        # another person who is an AND-CS client: only a spouse or parent can
        # have income deemed, and co_state_supplement_deemed_income finds
        # them in those groups. Skipping Medicaid when no one needs it avoids
        # computing enrollment for nothing.
        client = person("co_state_supplement_eligible", period)
        near_client = (
            (person.marital_unit.sum(client) - client > 0)
            | (person.tax_unit.sum(client) - client > 0)
            | (person.household.sum(client) - client > 0)
        )
        needs_medicaid = near_client & within_limit & ~exempt
        if not needs_medicaid.any():
            return exempt
        medicaid = person("co_adult_financial_medicaid_enrolled", period.this_year)
        return exempt | (needs_medicaid & medicaid)
