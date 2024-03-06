from policyengine_us.model_api import *


class nc_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina additions to the adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC
