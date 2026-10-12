from policyengine_us.model_api import *


class KYCCAPChildAgeCategory(Enum):
    INFANT_TODDLER = "Infant/Toddler (under 3 years)"
    PRESCHOOL = "Preschool (3 to under 6 years)"
    SCHOOL_AGE = "School-age (6 years and older)"


class ky_ccap_child_age_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = KYCCAPChildAgeCategory
    default_value = KYCCAPChildAgeCategory.PRESCHOOL
    definition_period = MONTH
    label = "Kentucky CCAP child age category"
    defined_for = StateCode.KY
    reference = "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=2"

    def formula(person, period, parameters):
        # DCC-300 collapses Infant (under 1) and Toddler (1 to under 3) into a
        # single Infant/Toddler rate column. 922 KAR 2:160 Section 1(18), (22),
        # (29), (33) define the age boundaries.
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.ky.dcbs.ccap.age_group
        return p.months.calc(age_in_months)
