from policyengine_us.model_api import *


class KSCCAPCenterAgeGroup(Enum):
    INFANT = "Infant (0-11 months)"
    TODDLER = "Toddler (12-35 months)"
    PRESCHOOL = "Preschool (36-59 months)"
    SCHOOL_AGE = "School-Age (60+ months)"


class ks_ccap_center_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = KSCCAPCenterAgeGroup
    default_value = KSCCAPCenterAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    label = "Kansas CCAP child care center age group"
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/appendix/c-18_providerratecht.pdf#page=8"
    )

    def formula(person, period, parameters):
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.ks.dcf.ccap.age_group
        return p.center_months.calc(age_in_months)
