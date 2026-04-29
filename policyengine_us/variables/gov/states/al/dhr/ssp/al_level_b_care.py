from policyengine_us.model_api import *


class al_level_b_care(Variable):
    value_type = bool
    entity = Person
    label = "Alabama SSP Independent Homelife Care Level B"
    definition_period = MONTH
    defined_for = StateCode.AL
    default_value = False
    reference = "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=10"
    documentation = """
    Level B care provides a lower supplement ($56/month vs $60/month for Level A)
    within the Independent Homelife Care category. When a person is in a
    private home or personal care home with IHC (al_ssp_care_setting =
    PRIVATE_HOME_IHC), this flag distinguishes Level B from Level A.
    """
