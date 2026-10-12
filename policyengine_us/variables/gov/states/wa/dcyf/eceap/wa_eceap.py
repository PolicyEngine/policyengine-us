from policyengine_us.model_api import *


class wa_eceap(Variable):
    value_type = float
    entity = Person
    label = "Washington ECEAP"
    unit = USD
    definition_period = YEAR
    defined_for = "wa_eceap_eligible"
    reference = "https://www.dcyf.wa.gov/services/early-learning-providers/eceap/community-funded-eceap/funding"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.dcyf.eceap
        slot_type = person("wa_eceap_slot_type", period)
        return p.per_slot_rate[slot_type]
