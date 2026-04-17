from policyengine_us.model_api import *


class PACCWProviderType(Enum):
    CENTER = "Center"
    GROUP = "Group"
    FAMILY = "Family"
    R_N = "Relative/Neighbor"


class pa_ccw_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = PACCWProviderType
    default_value = PACCWProviderType.CENTER
    definition_period = MONTH
    label = "Pennsylvania CCW child care provider type"
    defined_for = StateCode.PA
    reference = (
        "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=10",
    )
