from policyengine_us.model_api import *


class NYCCAPAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOLER = "Preschooler"
    SCHOOL_AGE = "School age"


class ny_ccap_age_group(Variable):
    value_type = Enum
    possible_values = NYCCAPAgeGroup
    default_value = NYCCAPAgeGroup.SCHOOL_AGE
    entity = Person
    label = "New York CCAP market-rate age group"
    definition_period = YEAR
    defined_for = StateCode.NY
    documentation = (
        "24-OCFS-LCM-22 sets a lower infant ceiling for center-based "
        "providers — day care centers, school-age child care programs and "
        "legally exempt group programs — than for home-based providers. The "
        "school-age band has no upper bound: a child over 12 who still meets "
        "the 415.1(b) definition of an eligible child draws the 6-12 rate."
    )
    reference = (
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=4"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.age_groups
        age = person("age", period)
        provider_type = person("childcare_provider_type_group", period)
        provider_types = provider_type.possible_values
        # The center/home split is inlined rather than read from
        # is_ccdf_home_based, which treats legally exempt group programs as
        # home-based. 24-OCFS-LCM-22 counts them as center-based.
        uses_center_age_groups = (provider_type == provider_types.DCC_SACC) | (
            provider_type == provider_types.LE_GC
        )
        infant_upper_bound = where(
            uses_center_age_groups,
            p.center_infant_upper_bound,
            p.home_infant_upper_bound,
        )
        return select(
            [
                age < infant_upper_bound,
                age < p.toddler_upper_bound,
                age < p.preschool_upper_bound,
            ],
            [
                NYCCAPAgeGroup.INFANT,
                NYCCAPAgeGroup.TODDLER,
                NYCCAPAgeGroup.PRESCHOOLER,
            ],
            default=NYCCAPAgeGroup.SCHOOL_AGE,
        )
