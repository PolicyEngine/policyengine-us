from policyengine_us.model_api import *


class CaChildCareProviderCategory(Enum):
    CHILD_CARE_CENTER = "Child care center"
    FAMILY_CHILD_CARE_HOME = "Family and child care home"
    LICENSE_EXEMPT = "License exempt"


class ca_child_care_provider_category(Variable):
    value_type = Enum
    possible_values = CaChildCareProviderCategory
    default_value = CaChildCareProviderCategory.CHILD_CARE_CENTER
    entity = Person
    label = "California CalWORKs Child Care provider categroy"
    definition_period = YEAR
    defined_for = StateCode.CA
