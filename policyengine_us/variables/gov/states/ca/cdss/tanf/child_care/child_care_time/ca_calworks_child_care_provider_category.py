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
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12"
