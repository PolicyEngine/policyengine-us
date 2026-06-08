from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.ccdf.ccdf_duration_of_care import (
    CCDFDurationOfCare,
)


class IDICCPTimeCategory(Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"


class id_iccp_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = IDICCPTimeCategory
    default_value = IDICCPTimeCategory.FULL_TIME
    definition_period = MONTH
    label = "Idaho Child Care Program time category"
    defined_for = StateCode.ID
    reference = "https://publicdocuments.dhw.idaho.gov/WebLink/DocView.aspx?dbid=0&id=19508&repo=PUBLIC-DOCUMENTS#page=1"

    def formula(person, period, parameters):
        duration = person("ccdf_duration_of_care", period.this_year)
        return where(
            duration == CCDFDurationOfCare.WEEKLY,
            IDICCPTimeCategory.FULL_TIME,
            IDICCPTimeCategory.PART_TIME,
        )
