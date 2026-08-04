from policyengine_us.model_api import *


class NVCCDPProviderType(Enum):
    CENTER = "Child Care Center"
    FCC = "Family Child Care"


class nv_ccdp_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = NVCCDPProviderType
    default_value = NVCCDPProviderType.CENTER
    definition_period = MONTH
    label = "Nevada CCDP child care provider type"
    defined_for = StateCode.NV
    reference = "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/ACF-118_CCDF_FFY_2025-2027_For_Nevada__3.pdf#page=54"
