from policyengine_us.model_api import *


class AgeGroup(Enum):
    INFANT = "Infant"
    TWO_YEAR_OLD = "2 Year olds"
    THREE_TO_FIVE_YEAR_OLD = "3 - 5 Year olds"
    SCHOOL_AGE = "School age"

class scca_age_group(Variable):
    value_type = Enum
    possible_values = AgeGroup
    default_value = AgeGroup.INFANT
    entity = Person
    label = "NC SCCA age group"
    definition_period = YEAR
    reference = ("https://docs.google.com/spreadsheets/d/1y7p8qkiOrMAM42rtSwT_ZXeA5tzew4edNkrTXACxf4M/edit?gid=1339413807#gid=1339413807"
                 "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/M/Market_Rates_Centers_Eff_10-1.pdf?ver=9w52alSPhmrmo0N9gGVMEw%3d%3d"
                "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/M/Mkt_Rates_Homes_eff_10-1.pdf?ver=baC5Yg7ZMrQ5fck2y9CcvA==")

    def formula(person, period, parameters):
        age = person("age", period)

        return select(
            [
                age < 2,
                age < 3,
                age >= 3 & age < 6,
                age < 17,
            ],
            [
                AgeGroup.INFANT,
                AgeGroup.TWO_YEAR_OLD,
                AgeGroup.THREE_TO_FIVE_YEAR_OLD,
                AgeGroup.SCHOOL_AGE,
            ],
        )
