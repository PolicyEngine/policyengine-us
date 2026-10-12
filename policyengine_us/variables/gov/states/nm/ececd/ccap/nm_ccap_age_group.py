from policyengine_us.model_api import *


class NMCCAPAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class nm_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = NMCCAPAgeGroup
    default_value = NMCCAPAgeGroup.PRESCHOOL
    definition_period = MONTH
    label = "New Mexico CCAP child age group"
    defined_for = StateCode.NM
    reference = "https://www.srca.nm.gov/parts/title08/08.015.0002.html"

    def formula(person, period, parameters):
        # age is a YEAR variable; convert to months to look up the age group.
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.nm.ececd.ccap.rates.age_group
        return p.months.calc(age_in_months)
