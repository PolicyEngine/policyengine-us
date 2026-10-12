from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_state_supplement,
)


class ri_ssp(Variable):
    value_type = float
    entity = Person
    label = "Rhode Island State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.RI
    reference = (
        "https://rules.sos.ri.gov/regulations/Part/218-20-00-5",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#l",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.dhs.ssp
        arrangement = person("ri_ssp_living_arrangement", period)
        arrangements = arrangement.possible_values
        care = arrangement == arrangements.RESIDENTIAL_CARE
        individual = p.amount.individual[arrangement]
        couple = p.amount.couple[arrangement]
        payment = ssi_state_supplement(
            person, period, parameters, individual, couple, federal_payment_rules=care
        )
        return payment
