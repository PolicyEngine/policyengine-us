from policyengine_us.model_api import *


class IASSALivingArrangementInput(Enum):
    NONE = "Not in a qualifying arrangement"
    FAMILY_LIFE_HOME = "Resides in certified family-life home"
    RESIDENTIAL_CARE_FACILITY = "Resides in licensed residential care facility"
    IN_HOME_HEALTH_RELATED_CARE = "Receives in-home health-related care"


class ia_ssa_living_arrangement_input(Variable):
    value_type = Enum
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA living-arrangement input"
    possible_values = IASSALivingArrangementInput
    default_value = IASSALivingArrangementInput.NONE
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.52.pdf#page=1",
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.177.pdf#page=2",
        "https://www.legis.iowa.gov/docs/code/135C.1.pdf",
    )
