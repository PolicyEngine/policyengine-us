from policyengine_us.model_api import *


class pa_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF countable resources"
    defined_for = StateCode.PA
    unit = USD
    definition_period = YEAR
