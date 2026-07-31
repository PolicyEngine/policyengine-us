from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ne.dhhs.child_care_subsidy.ne_child_care_subsidy_rate_unit import (
    NEChildCareSubsidyRateUnit,
)


class ne_child_care_subsidy_authorized_rate_unit(Variable):
    value_type = Enum
    entity = Person
    possible_values = NEChildCareSubsidyRateUnit
    default_value = NEChildCareSubsidyRateUnit.NONE
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy administrative authorized rate unit"
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Documents/CC-Subsidy-Provider-Booklet.pdf#page=31",
    )
