from policyengine_us.model_api import *


class nm_ssi_state_supplement(Variable):
    value_type = float
    entity = Person
    label = "New Mexico SSI state supplement"
    definition_period = YEAR
    defined_for = "nm_ssi_state_supplement_eligible"
    unit = USD
    reference = "https://srca.nm.gov/parts/title08/08.106.0500.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nm.hca.ssi_supplement
        return p.amount * MONTHS_IN_YEAR
