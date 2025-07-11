from policyengine_us.model_api import *


class DCCCSPSCHEDULETYPE(Enum):
    FULL_TIME_TRADITIONAL = "Full-Time Traditional"
    PART_TIME_TRADITIONAL = "Part-Time Traditional"
    EXTENDED_DAY_FULL_TIME = "Extended Day Full-Time"
    EXTENDED_DAY_PART_TIME = "Extended Day Part-Time"
    FULL_TIME_NONTRADITIONAL = "Full-Time Nontraditional"
    PART_TIME_NONTRADITIONAL = "Part-Time Nontraditional"


class dc_ccsp_schedule_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = DCCCSPSCHEDULETYPE
    default_value = DCCCSPSCHEDULETYPE.FULL_TIME_TRADITIONAL
    label = "DC Child Care Subsidy Program (CCSP) schedule type"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/FY25%20Subsidy%20Reimbursement%20Rates%20English.pdf"
