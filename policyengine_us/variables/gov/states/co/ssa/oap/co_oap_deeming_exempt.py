from policyengine_us.model_api import *


class co_oap_deeming_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Colorado Old Age Pension spouse income not deemed"
    definition_period = MONTH
    defined_for = StateCode.CO
    # PDF page 78
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=78"

    def formula(person, period, parameters):
        # 9 CCR 2503-5 3.534(C): the income of a spouse who receives Adult
        # Financial grant payments, SSI or Medicaid "and has income no greater
        # than the OAP limit" is not deemed to the OAP client.
        p = parameters(period).gov.states.co.ssa.oap
        ssi = person("ssi", period)
        # The rule does not define the OAP limit. We read it as the OAP grant
        # standard, against the spouse's own total countable income under
        # 3.533, SSI included.
        income = person("co_oap_own_countable_income", period) + ssi
        within_limit = income <= p.grant_standard
        receives_ssi = (ssi > 0) | person("receives_ssi", period)
        # Old Age Pension is the Adult Financial program modeled for someone
        # who is not on SSI; AND-CS requires SSI. Receipt is judged on the
        # spouse's own income: when both spouses are OAP clients within the
        # limit, neither one's income is deemed to the other.
        year = period.this_year
        receives_oap = person("co_oap_eligible", year) & (income < p.grant_standard)
        # SNAP counts OAP as income, so Medicaid enrollment is read without
        # SNAP's community-engagement pass-through to avoid a cycle.
        medicaid = person("medicaid_enrolled_for_ssi_state_supplement", year)
        return (receives_ssi | receives_oap | medicaid) & within_limit
