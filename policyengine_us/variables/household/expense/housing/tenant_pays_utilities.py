from policyengine_us.model_api import *


class tenant_pays_utilities(Variable):
    value_type = bool
    entity = Household
    label = "Whether the tenant is responsible for utility payments"
    documentation = (
        "Whether the household pays its own utilities rather than having them "
        "bundled into rent. Defaults to true, the common lease arrangement. Set "
        "it to false only when the household holds no utility account of its "
        "own because all utilities are included in rent; a household that pays "
        "its own electric bill but has water, sewer, or trash in rent stays "
        "true. The HUD utility allowance is available only when the tenant pays "
        "utilities, and utilities_included_in_rent is derived as the inverse of "
        "this input."
    )
    definition_period = YEAR
    default_value = True
    reference = "https://www.law.cornell.edu/cfr/text/24/982.517"
