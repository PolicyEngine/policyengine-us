from policyengine_us.model_api import *


class NJSSPCareSetting(Enum):
    CONGREGATE_CARE = "New Jersey certified congregate care"
    RESIDENTIAL_HEALTH_CARE = "New Jersey certified residential health care"
    EXCLUDED = "Setting excluded from New Jersey supplementation"
    NONE = "No certified care setting"


class nj_ssp_care_setting(Variable):
    value_type = Enum
    entity = Person
    label = "New Jersey SSP certified care setting"
    definition_period = MONTH
    possible_values = NJSSPCareSetting
    default_value = NJSSPCareSetting.NONE
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501415025NY"
    documentation = """
    Certified settings require inclusion in New Jersey's Congregate Care
    Directory. EXCLUDED includes publicly operated community residences,
    emergency shelters and institutional children funded by private insurance.
    Use the SSI claim and marital-unit inputs to represent separate individual
    claims after institutionalization; this input does not change federal SSI.
    """
