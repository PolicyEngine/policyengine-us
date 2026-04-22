from policyengine_us.model_api import *


class SCCCAPAgeGroup(Enum):
    UNDER_1 = "Under 1"
    AGE_1 = "Age 1"
    AGE_2 = "Age 2"
    AGE_3 = "Age 3"
    AGE_4 = "Age 4"
    AGE_5_NOT_IN_K = "Age 5, Not in Kindergarten"
    AGE_5_12_IN_SCHOOL = "Age 5-12, In School"


class sc_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = SCCCAPAgeGroup
    default_value = SCCCAPAgeGroup.AGE_5_12_IN_SCHOOL
    definition_period = MONTH
    label = "South Carolina CCAP child age group for payment rates"
    defined_for = StateCode.SC
    reference = "https://www.scchildcare.org/media/vwybydmg/child-care-scholarship-maximum-payments-allowed-ffy2023-pdf.pdf#page=1"

    def formula(person, period, parameters):
        age = person("age", period.this_year)
        is_in_school = person("is_in_k12_school", period.this_year)
        p = parameters(period).gov.states.sc.dss.ccap.age_group
        age_index = p.age.calc(age)
        # age_index 0-4 map directly to UNDER_1 through AGE_4.
        # age_index 5 = exactly age 5: if in school -> AGE_5_12_IN_SCHOOL (6),
        # else -> AGE_5_NOT_IN_K (5).
        # age_index 6 = age 6+: always AGE_5_12_IN_SCHOOL (6).
        return where(
            (age_index == 5) & ~is_in_school,
            5,
            where(age_index >= 5, 6, age_index),
        )
