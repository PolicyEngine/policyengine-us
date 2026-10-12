from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_state_supplement,
)


class vt_aabd_federal(Variable):
    value_type = float
    entity = Person
    label = "Vermont federally administered AABD supplement"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.VT
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501415058#m"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.vt.dcf.aabd.amount
        arrangement = person("vt_aabd_living_arrangement", period)
        return ssi_state_supplement(
            person, period, parameters, p.individual[arrangement], p.couple[arrangement]
        )
