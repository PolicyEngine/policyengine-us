from policyengine_us.model_api import *


class aca_slspc_ca(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second-lowest ACA silver-plan cost for taxunit in California"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    adds = ["person_aca_slspc_ca"]
