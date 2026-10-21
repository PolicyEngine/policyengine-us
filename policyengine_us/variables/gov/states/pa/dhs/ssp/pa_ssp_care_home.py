from policyengine_us.model_api import *


class PASSPCareHome(Enum):
    DOMICILIARY_CARE = "State-certified domiciliary care home"
    PERSONAL_CARE = "Licensed personal care home, certified for the supplement"
    NONE = "Not in a certified care home"


class pa_ssp_care_home(Variable):
    value_type = Enum
    entity = Person
    label = "Pennsylvania SSP certified care home"
    definition_period = MONTH
    defined_for = StateCode.PA
    possible_values = PASSPCareHome
    default_value = PASSPCareHome.NONE
    reference = (
        "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter299/s299.1.html",
        "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter299/s299.22.html",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#k1",
    )
