from policyengine_us.model_api import *


class tenant_pays_utilities(Variable):
    value_type = bool
    entity = Household
    label = "Whether the tenant is responsible for utility payments"
    documentation = "Whether the household pays its own utilities rather than having them bundled into rent. Defaults to true, the common lease arrangement; set it to false when utilities are included in rent. The HUD utility allowance is available only when the tenant pays utilities, and utilities_included_in_rent is derived as the inverse of this input."
    definition_period = YEAR
    default_value = True
    reference = "https://www.law.cornell.edu/cfr/text/24/982.517"
