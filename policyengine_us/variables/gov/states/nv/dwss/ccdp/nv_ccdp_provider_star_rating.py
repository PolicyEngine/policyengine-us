from policyengine_us.model_api import *


class NVCCDPProviderStarRating(Enum):
    STAR_1 = "1 Star"
    STAR_2 = "2 Stars"
    STAR_3 = "3 Stars"
    STAR_4 = "4 Stars"
    STAR_5 = "5 Stars"


class nv_ccdp_provider_star_rating(Variable):
    value_type = Enum
    entity = Person
    possible_values = NVCCDPProviderStarRating
    default_value = NVCCDPProviderStarRating.STAR_1
    definition_period = MONTH
    label = "Nevada CCDP child care provider Silver State Stars rating"
    defined_for = StateCode.NV
    reference = "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/Child_Care_Manual_July_2024.pdf#page=107"
