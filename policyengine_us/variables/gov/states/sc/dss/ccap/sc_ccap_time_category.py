from policyengine_us.model_api import *


class SCCCAPTimeCategory(Enum):
    HALF_TIME = "Half Time"
    FULL_TIME = "Full Time"


class sc_ccap_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = SCCCAPTimeCategory
    default_value = SCCCAPTimeCategory.FULL_TIME
    definition_period = MONTH
    label = "South Carolina CCAP care schedule category"
    defined_for = StateCode.SC
    reference = "https://www.scchildcare.org/media/vwybydmg/child-care-scholarship-maximum-payments-allowed-ffy2023-pdf.pdf#page=1"

    def formula(person, period, parameters):
        hours = person("childcare_hours_per_week", period.this_year)
        p = parameters(period).gov.states.sc.dss.ccap.time_category
        standard_category = p.hours.calc(hours)
        # Per Section 2.15, Head Start children are paid part-time
        # while enrolled to extend the Head Start day.
        is_head_start = person("is_enrolled_in_head_start", period.this_year)
        return where(
            is_head_start,
            SCCCAPTimeCategory.HALF_TIME,
            standard_category,
        )
