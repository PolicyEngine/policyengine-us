from policyengine_us.model_api import *


class IllinoisCCAPAgeCategory(Enum):
    UNDER_AGE_2 = "Under age 2"
    AGE_2 = "Age 2"
    AGE_3_AND_OLDER = "Age 3 and older"


class il_ccap_day_care_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = IllinoisCCAPAgeCategory
    default_value = IllinoisCCAPAgeCategory.NONE
    definition_period = MONTH
    label = "Illinois Child Care Assistance Program (CCAP) age category"
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=163817"

    # def formula(person, period, parameters):
    #     eligible_child = person("il_ccap_eligible_child", period)
    #     age = person("monthly_age", period)
    #     under_age_2 = age < 2
    #     age_2 = age == 2
    #     age_3_and_older = age >= 3
    #     conditions = eligible_child & [under_age_2, age_2, age_3_and_older]
    #     results = [
    #         IllinoisCCAPAgeCategory.UNDER_AGE_2,
    #         IllinoisCCAPAgeCategory.AGE_2,
    #         IllinoisCCAPAgeCategory.AGE_3_AND_OLDER,
    #     ]
    #     return select(
    #         conditions,
    #         results,
    #         default=IllinoisCCAPAgeCategory.UNDER_AGE_2,
    #     )
