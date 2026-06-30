from policyengine_us.model_api import *


class IASSADPConfiguration(Enum):
    AGED_OR_DISABLED_WITH_DEPENDENT = "Aged/disabled client with dependent relative"
    AGED_OR_DISABLED_WITH_SPOUSE_AND_DEPENDENT = (
        "Aged/disabled client with aged/disabled spouse and dependent relative"
    )
    BLIND_WITH_DEPENDENT = "Blind client with dependent relative"
    BLIND_WITH_AGED_OR_DISABLED_SPOUSE_AND_DEPENDENT = (
        "Blind client with aged/disabled spouse and dependent relative"
    )
    BLIND_WITH_BLIND_SPOUSE_AND_DEPENDENT = (
        "Blind client with blind spouse and dependent relative"
    )
    NONE = "Not in a dependent person configuration"


class ia_ssa_dp_configuration(Variable):
    value_type = Enum
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA dependent person configuration"
    possible_values = IASSADPConfiguration
    default_value = IASSADPConfiguration.NONE
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.52.pdf#page=1",
        "https://hhs.iowa.gov/assistance-programs/state-supplementary-assistance",
    )
