from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.me.dhhs.ssp.me_ssp_living_arrangement import (
    MESSPLivingArrangement,
)


class me_ssp_living_arrangement_input(Variable):
    value_type = Enum
    entity = Person
    label = "Maine SSP living arrangement (state-specified)"
    definition_period = MONTH
    defined_for = StateCode.ME
    possible_values = MESSPLivingArrangement
    default_value = MESSPLivingArrangement.LIVING_ALONE_OR_WITH_OTHERS
    reference = (
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/144c332-2025-101%20%28AMD%29_0.docx",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/content/assets/144c332-appendices-charts.docx",
    )
