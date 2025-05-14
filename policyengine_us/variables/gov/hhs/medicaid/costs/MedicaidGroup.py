from policyengine_us.model_api import *


class MedicaidGroup(Enum):
    """High‑level eligibility groups for per‑capita cost analysis."""

    CHILD = "CHILD"
    NON_EXPANSION_ADULT = "NON_EXPANSION_ADULT"
    EXPANSION_ADULT = "EXPANSION_ADULT"
    AGED_DISABLED = "AGED_DISABLED"
    NONE = "NONE"  # fallback for ineligible or uncategorised persons
