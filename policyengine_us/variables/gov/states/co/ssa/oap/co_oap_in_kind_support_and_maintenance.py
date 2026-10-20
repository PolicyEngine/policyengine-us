from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ssa.oap._precision import (
    cents,
    ssi_paid,
)


class co_oap_in_kind_support_and_maintenance(Variable):
    value_type = float
    entity = Person
    label = "Colorado Old Age Pension in-kind support and maintenance"
    unit = USD
    definition_period = MONTH
    # PDF pages 72-73
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=72"

    def formula(person, period, parameters):
        # 9 CCR 2503-5 3.520.79(B)(6): an SSI recipient charged in-kind support
        # and maintenance by SSA is charged a matching ISM, counted as unearned
        # income. A joint couple's ISM is one presumed maximum value for the
        # couple, which SSI splits equally between the spouses. ISM through
        # SSA's one-third reduction, and Colorado's own ISM for a client not
        # on SSI (3.520.79(C)), are not modeled.
        ism = person("ssi_in_kind_support_and_maintenance", period)
        couple_computation = person("ssi_couple_computation_applies", period)
        ssi = ssi_paid(person("ssi", period))
        receives_ssi = (ssi > 0) | person("receives_ssi", period)
        ism = where(couple_computation, ism / 2, ism) * receives_ssi
        return cents(ism)
