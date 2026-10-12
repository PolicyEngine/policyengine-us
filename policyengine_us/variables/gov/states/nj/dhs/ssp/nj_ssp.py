from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_state_supplement,
)


class nj_ssp(Variable):
    value_type = float
    entity = Person
    label = "New Jersey State Supplementary Payment"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NJ
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#j",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415025NY",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320430#D",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.dhs.ssp.amount
        arrangement = person("nj_ssp_living_arrangement", period)
        return ssi_state_supplement(
            person, period, parameters, p.individual[arrangement], p.couple[arrangement]
        )
