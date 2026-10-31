from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ssa.oap._spouses import (
    co_oap_couple_total,
)
from policyengine_us.variables.gov.states.co.ssa.oap._precision import (
    PRECISION,
    ssi_paid,
)


class co_oap_deeming_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Colorado Old Age Pension client's spouse whose income is not deemed"
    documentation = (
        "True for the spouse of an Old Age Pension-eligible client when "
        "3.534(C) keeps the spouse's income from being deemed; false for "
        "everyone else."
    )
    definition_period = MONTH
    # Not restricted to Colorado: 3.534(C) sets no residence condition on the
    # spouse.
    # PDF page 78
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=78"

    def formula(person, period, parameters):
        # 9 CCR 2503-5 3.534(C): the income of a spouse who receives Adult
        # Financial grant payments, SSI or Medicaid "and has income no greater
        # than the OAP limit" is not deemed to the OAP client.
        p = parameters(period).gov.states.co.ssa.oap
        ssi = ssi_paid(person("ssi", period))
        # The rule does not define the OAP limit. We read it as the OAP grant
        # standard, against the spouse's own total countable income under
        # 3.533, SSI included.
        income = person("co_oap_own_countable_income", period) + ssi
        within_limit = income <= p.grant_standard + PRECISION
        receives_ssi = (ssi > 0) | person("receives_ssi", period)
        # Old Age Pension is the Adult Financial program modeled for someone
        # who is not on SSI; AND-CS requires SSI. Receipt is judged on the
        # spouse's own income, as co_oap judges a positive grant: when both
        # spouses are OAP clients within the limit, neither one's income is
        # deemed to the other. (A reading in which neither receives OAP, and
        # each one's income is deemed to the other, can also be
        # self-consistent; the model takes the one in which both are paid.)
        year = period.this_year
        eligible = person("co_oap_eligible", year)
        receives_oap = eligible & (p.grant_standard - income > PRECISION)
        spouse_of_client = (
            co_oap_couple_total(person, year, eligible.astype(int)) - eligible > 0
        )
        candidate = spouse_of_client & within_limit
        exempt = candidate & (receives_ssi | receives_oap)
        # Medicaid decides only for a candidate not exempt otherwise. Skipping
        # it when no one needs it avoids computing Medicaid enrollment for
        # nothing.
        needs_medicaid = candidate & ~exempt
        if not needs_medicaid.any():
            return exempt
        medicaid = person("co_oap_medicaid_enrolled", year)
        return exempt | (needs_medicaid & medicaid)
