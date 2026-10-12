from policyengine_us.model_api import *


class MNCCAPProviderType(Enum):
    FAMILY_CHILD_CARE = "Family child care"
    CHILD_CARE_CENTER = "Child care center"
    LICENSE_EXEMPT = "License-exempt program"
    LEGAL_NON_LICENSED = "Legal non-licensed provider"


class mn_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = MNCCAPProviderType
    default_value = MNCCAPProviderType.CHILD_CARE_CENTER
    definition_period = MONTH
    label = "Minnesota CCAP child care provider type"
    defined_for = StateCode.MN
    reference = (
        # Minn. Stat. 142E.17 subd. 1 — provider categories and rates.
        "https://www.revisor.mn.gov/statutes/cite/142E.17",
    )
