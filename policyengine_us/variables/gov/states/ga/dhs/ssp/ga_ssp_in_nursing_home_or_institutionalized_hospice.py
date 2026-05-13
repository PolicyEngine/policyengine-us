from policyengine_us.model_api import *


class ga_ssp_in_nursing_home_or_institutionalized_hospice(Variable):
    value_type = bool
    entity = Person
    label = "Georgia SSP recipient is in a nursing home or institutionalized hospice"
    definition_period = YEAR
    defined_for = StateCode.GA
    default_value = False
    reference = (
        "https://pamms.dhs.ga.gov/dfcs/medicaid/2578/",
        "https://pamms.dhs.ga.gov/dfcs/medicaid/2136/",
    )
