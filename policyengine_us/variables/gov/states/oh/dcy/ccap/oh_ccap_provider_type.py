from policyengine_us.model_api import *


class OHCCAPProviderType(Enum):
    # Centers, day camps, preschool/school-age programs, and ODE programs.
    CENTER = "Center"
    # Licensed type A and type B homes and in-home aides.
    HOME = "Home"


class oh_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = OHCCAPProviderType
    default_value = OHCCAPProviderType.CENTER
    definition_period = MONTH
    label = "Ohio CCAP child care provider type"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-10"
