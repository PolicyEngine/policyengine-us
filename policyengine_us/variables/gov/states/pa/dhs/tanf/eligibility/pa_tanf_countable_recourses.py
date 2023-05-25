from policyengine_us.model_api import *


class pa_tanf_countable_recourses(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA TANF countable resources"
    defined_for = StateCode.PA
    unit = USD
    definition_period = YEAR
