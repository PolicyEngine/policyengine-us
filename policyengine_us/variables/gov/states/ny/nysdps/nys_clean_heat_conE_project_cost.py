from policyengine_us.model_api import *


class nys_clean_heat_project_cost(Variable):
    value_type = float
    entity = TaxUnit
    label = "Clean Heat Project Cost"
    documentation = ""
    unit = USD
    definition_period = YEAR
    reference = "url"
    defined_for = StateCode.NY