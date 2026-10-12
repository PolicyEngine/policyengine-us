from policyengine_us.model_api import *


class WAWCCCFamilyHomeAgeGroup(Enum):
    INFANT = "Infant"
    ENHANCED_TODDLER = "Enhanced Toddler"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class wa_wccc_family_home_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = WAWCCCFamilyHomeAgeGroup
    default_value = WAWCCCFamilyHomeAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    defined_for = StateCode.WA
    label = "Washington WCCC licensed family home age group"
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0205"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.dcyf.wccc.rates.age_groups
        age_years = person("monthly_age", period)
        age_months = age_years * MONTHS_IN_YEAR
        return select(
            [
                age_months < p.infant_max_months,
                age_months < p.enhanced_toddler_max_months,
                age_months < p.toddler_max_months,
                age_years < p.preschool_max_years,
            ],
            [
                WAWCCCFamilyHomeAgeGroup.INFANT,
                WAWCCCFamilyHomeAgeGroup.ENHANCED_TODDLER,
                WAWCCCFamilyHomeAgeGroup.TODDLER,
                WAWCCCFamilyHomeAgeGroup.PRESCHOOL,
            ],
            default=WAWCCCFamilyHomeAgeGroup.SCHOOL_AGE,
        )
