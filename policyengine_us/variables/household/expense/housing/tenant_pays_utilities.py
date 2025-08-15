from policyengine_us.model_api import *


class tenant_pays_utilities(Variable):
    value_type = bool
    entity = Household
    label = "Whether the tenant is responsible for utility payments"
    definition_period = YEAR
