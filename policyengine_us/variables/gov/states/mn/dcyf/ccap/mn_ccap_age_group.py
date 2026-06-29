from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mn.dcyf.ccap.mn_ccap_provider_type import (
    MNCCAPProviderType,
)


class MNCCAPAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School age"


class mn_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = MNCCAPAgeGroup
    default_value = MNCCAPAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    label = "Minnesota CCAP child age group"
    defined_for = StateCode.MN
    reference = (
        # Minn. Rules 9503.0005 — infant/toddler/preschool/school age
        # definitions, which differ between family child care and centers.
        "https://www.revisor.mn.gov/rules/9503.0005/",
    )

    def formula(person, period, parameters):
        # age is a float; the bracket parameters key on age in months.
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        provider_type = person("mn_ccap_provider_type", period)
        p = parameters(period).gov.states.mn.dcyf.ccap.age_group
        # Family child care and legal non-licensed providers use the family
        # child care age boundaries; centers and license-exempt programs (paid
        # at the center rate) use the center age boundaries. The bracket
        # parameters return the integer index into MNCCAPAgeGroup.
        is_family_boundary = (provider_type == MNCCAPProviderType.FAMILY_CHILD_CARE) | (
            provider_type == MNCCAPProviderType.LEGAL_NON_LICENSED
        )
        return where(
            is_family_boundary,
            p.family_months.calc(age_in_months),
            p.center_months.calc(age_in_months),
        )
