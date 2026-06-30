from policyengine_us.model_api import *


class MICCAPAgeGroup(Enum):
    # Declared in ordinal order so the age_group/thresholds bracket parameter
    # (0/1/2) maps directly to the Enum index.
    INFANT_TODDLER = "Infant/Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class mi_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = MICCAPAgeGroup
    default_value = MICCAPAgeGroup.INFANT_TODDLER
    definition_period = MONTH
    label = "Michigan CDC rate age group"
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/RF/Public/RFT/270.pdf#page=4"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mi.mdhhs.ccap.age_group
        age = person("age", period.this_year)
        return p.thresholds.calc(age)
