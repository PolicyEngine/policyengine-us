from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ne.dhhs.aabd.ne_aabd_living_arrangement import (
    NEAABDLivingArrangement,
)


class ne_aabd_alternate_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Nebraska AABD alternate (non-Medicaid) living arrangement"
    definition_period = YEAR
    defined_for = StateCode.NE
    possible_values = NEAABDLivingArrangement
    default_value = NEAABDLivingArrangement.INDEPENDENT
    reference = "https://dhhs.ne.gov/Documents/469-000-211.pdf"
