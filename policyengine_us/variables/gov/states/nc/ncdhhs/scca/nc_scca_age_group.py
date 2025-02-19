from policyengine_us.model_api import *


class NCSCCAAgeGroup(Enum):
    NOT_QUALIFY = "Not qualify"
    INFANT = "Infant"
    TWO_YEAR_OLD = "2 Year olds"
    THREE_TO_FIVE_YEAR_OLD = "3 - 5 Year olds"
    SCHOOL_AGE = "School age"


class nc_scca_age_group(Variable):
    value_type = Enum
    possible_values = NCSCCAAgeGroup
    default_value = NCSCCAAgeGroup.NOT_QUALIFY
    entity = Person
    label = "North Carolina SCCA age group"
    definition_period = YEAR
    reference = (
        "https://docs.google.com/spreadsheets/d/1y7p8qkiOrMAM42rtSwT_ZXeA5tzew4edNkrTXACxf4M/edit?gid=1339413807#gid=1339413807"
        "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/M/Market_Rates_Centers_Eff_10-1.pdf?ver=9w52alSPhmrmo0N9gGVMEw%3d%3d"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.scca
        age = person("age", period)
        disabled = person("is_disabled", period)

        return select(
            [
                age >= p.disabled_age_limit,
                age < p.infant_age_limit,
                age < p.toddler_age_limit,
                (age >= p.preschool_age_lower) & (age < p.preschool_age_upper),
                (age < p.school_age_limit)
                | ((age < p.disabled_age_limit) & disabled),
            ],
            [
                NCSCCAAgeGroup.NOT_QUALIFY,
                NCSCCAAgeGroup.INFANT,
                NCSCCAAgeGroup.TWO_YEAR_OLD,
                NCSCCAAgeGroup.THREE_TO_FIVE_YEAR_OLD,
                NCSCCAAgeGroup.SCHOOL_AGE,
            ],
            default=NCSCCAAgeGroup.NOT_QUALIFY,
        )
