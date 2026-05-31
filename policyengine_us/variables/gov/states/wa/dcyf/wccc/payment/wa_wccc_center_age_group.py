from policyengine_us.model_api import *


class WAWCCCCenterAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class wa_wccc_center_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = WAWCCCCenterAgeGroup
    default_value = WAWCCCCenterAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    defined_for = StateCode.WA
    label = "Washington WCCC licensed center age group"
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0200"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.dcyf.wccc.rates.age_groups
        age_years = person("monthly_age", period)
        age_months = age_years * MONTHS_IN_YEAR
        return select(
            [
                age_months < p.infant_max_months,
                age_months < p.toddler_max_months,
                age_years < p.preschool_max_years,
            ],
            [
                WAWCCCCenterAgeGroup.INFANT,
                WAWCCCCenterAgeGroup.TODDLER,
                WAWCCCCenterAgeGroup.PRESCHOOL,
            ],
            default=WAWCCCCenterAgeGroup.SCHOOL_AGE,
        )
