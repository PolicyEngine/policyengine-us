from policyengine_us.model_api import *


class ALSSPCareSetting(Enum):
    NONE = "No qualifying Alabama SSP care setting"
    PRIVATE_HOME_IHC = "Private home or personal care home with IHC"
    FOSTER_HOME = "Foster home with IHC or specialized IHC"
    CEREBRAL_PALSY_CENTER = "Cerebral palsy treatment center"
    NURSING_FACILITY = "Nursing facility / FCMP nursing care"


class al_ssp_care_setting(Variable):
    value_type = Enum
    entity = Person
    label = "Alabama SSP care setting"
    definition_period = MONTH
    defined_for = StateCode.AL
    possible_values = ALSSPCareSetting
    default_value = ALSSPCareSetting.NONE
    reference = (
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=9",
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=10",
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=14",
    )
    documentation = """
    This variable classifies the care setting only. Current eligibility for
    private-home and foster-home arrangements also depends on the Elderly/
    Disabled Medicaid Waiver and SNF-criteria flags, unless the case is modeled
    through the grandfathered override.
    """
