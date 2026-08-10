from policyengine_us.model_api import *


class SDCCATimeCategory(Enum):
    FULL_TIME = "Full time"
    PART_TIME = "Part time"
    LIMITED_TIME = "Limited time"


class sd_cca_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = SDCCATimeCategory
    default_value = SDCCATimeCategory.LIMITED_TIME
    definition_period = MONTH
    defined_for = StateCode.SD
    label = "South Dakota CCA level of service"
    reference = "https://dss.sd.gov/docs/childcare/assistance/CCA_Weekly_Reimbursement_Rates.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sd.dss.cca.time_category
        # Full-time care is 28 or more hours per week, part-time is 16 through
        # 27 hours, and limited-time is 1 through 15 hours.
        hours = person("childcare_hours_per_week", period.this_year)
        return select(
            [
                hours >= p.full_time_min_hours,
                hours >= p.part_time_min_hours,
            ],
            [SDCCATimeCategory.FULL_TIME, SDCCATimeCategory.PART_TIME],
            default=SDCCATimeCategory.LIMITED_TIME,
        )
