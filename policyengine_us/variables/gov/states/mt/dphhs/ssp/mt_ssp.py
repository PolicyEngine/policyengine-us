from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_state_supplement,
)


class mt_ssp(Variable):
    value_type = float
    entity = Person
    label = "Montana State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#h",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415010DEN",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-2025.htm",
    )

    def formula(person, period, parameters):
        state = person.household("state_code", period.this_year)
        resident = (state == StateCode.MT) | person("mt_ssp_in_state_custody", period)
        excluded = person("mt_ssp_receives_section_1619_benefits", period)
        category = person("mt_ssp_payment_category", period)
        p = parameters(period).gov.states.mt.dphhs.ssp.amount
        payment = ssi_state_supplement(
            person, period, parameters, p.individual[category], p.couple[category]
        )
        return resident * ~excluded * payment
