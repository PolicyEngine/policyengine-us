from policyengine_us.model_api import *


class NEChildCareSubsidyQualityTier(Enum):
    BASE = "Base licensed rate"
    ACCREDITED_STEP_3 = "Accredited or Step 3"
    STEP_4 = "Step 4"
    STEP_5 = "Step 5"
    NONE = "No quality tier reported"


class ne_child_care_subsidy_quality_tier(Variable):
    value_type = Enum
    entity = Person
    possible_values = NEChildCareSubsidyQualityTier
    default_value = NEChildCareSubsidyQualityTier.NONE
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy provider quality tier"
    defined_for = StateCode.NE
    reference = ("https://dhhs.ne.gov/Child%20Care%20Documents/Subsidy-Rates.pdf",)
