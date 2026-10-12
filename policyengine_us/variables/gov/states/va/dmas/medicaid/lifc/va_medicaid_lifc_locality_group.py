from policyengine_us.model_api import *


class VAMedicaidLIFCLocalityGroup(Enum):
    GROUP_I = "Group I"
    GROUP_II = "Group II"
    GROUP_III = "Group III"


class va_medicaid_lifc_locality_group(Variable):
    value_type = Enum
    possible_values = VAMedicaidLIFCLocalityGroup
    default_value = VAMedicaidLIFCLocalityGroup.GROUP_I
    entity = Household
    label = "Virginia Medicaid LIFC locality group"
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = "https://www.dmas.virginia.gov/media/0aynyhxk/m04-1-1-26a.pdf#page=52"

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.va.dmas.medicaid.lifc.localities
        # City tokens absent from County cannot match these lists and use the
        # Group I default.
        return select(
            [
                np.isin(county, p.group1),
                np.isin(county, p.group2),
                np.isin(county, p.group3),
            ],
            [
                VAMedicaidLIFCLocalityGroup.GROUP_I,
                VAMedicaidLIFCLocalityGroup.GROUP_II,
                VAMedicaidLIFCLocalityGroup.GROUP_III,
            ],
            default=VAMedicaidLIFCLocalityGroup.GROUP_I,
        )
