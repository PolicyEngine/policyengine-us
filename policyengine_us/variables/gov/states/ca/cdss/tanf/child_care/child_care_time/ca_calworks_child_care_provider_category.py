from policyengine_us.model_api import *


class CaCalworksChildCareProviderCategory(Enum):
    CHILD_CARE_CENTER = "Child care center"
    FAMILY_CHILD_CARE_HOME = "Family and child care home"
    LICENSE_EXEMPT = "License exempt"


class ca_calworks_child_care_provider_category(Variable):
    value_type = Enum
    possible_values = CaCalworksChildCareProviderCategory
    default_value = CaCalworksChildCareProviderCategory.CHILD_CARE_CENTER
    entity = Person
    label = "California CalWORKs Child Care provider categroy"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/child-care/regional-market-rate-ceilings.html"
