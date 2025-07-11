from policyengine_us.model_api import *


class DCCCSPChildCareProviderCategory(Enum):
    CHILD_CENTER = "Child Center"
    CHILD_HOME_AND_EXPANDED_HOME = "Child Home and Expanded Home"
    IN_HOME_CHILD_CARE = "In-Home Child Care"


class dc_ccsp_childcare_provider_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = DCCCSPChildCareProviderCategory
    default_value = DCCCSPChildCareProviderCategory.CHILD_CENTER
    label = "DC Child Care Subsidy Program (CCSP) child care provider category"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/FY25%20Subsidy%20Reimbursement%20Rates%20English.pdf"
