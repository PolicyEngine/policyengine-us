from policyengine_us.model_api import *


class NDCCAPProviderQRISStep(Enum):
    STEP_1 = "Step 1"
    STEP_2 = "Step 2"
    STEP_3 = "Step 3"
    STEP_4 = "Step 4"
    UNRATED = "Unrated"


class nd_ccap_provider_qris_step(Variable):
    value_type = Enum
    entity = Person
    possible_values = NDCCAPProviderQRISStep
    default_value = NDCCAPProviderQRISStep.UNRATED
    definition_period = MONTH
    label = "North Dakota CCAP provider QRIS step rating"
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"
