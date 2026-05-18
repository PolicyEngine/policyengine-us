from policyengine_us.model_api import *


class ALCCSPAgeCategory(Enum):
    INFANT_TODDLER = "Infant/Toddler (under 36 months)"
    PRESCHOOL = "Preschool (36-59 months)"
    SCHOOL_AGE = "School Age (60+ months)"


class al_ccsp_age_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = ALCCSPAgeCategory
    default_value = ALCCSPAgeCategory.INFANT_TODDLER
    definition_period = MONTH
    label = "Alabama CCSP child age category for payment rates"
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/Provider-Rates-with-QRIS-Tiers-April-1-2022-b.pdf#page=2"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dhr.ccsp.age_category
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        return p.months.calc(age_months)
