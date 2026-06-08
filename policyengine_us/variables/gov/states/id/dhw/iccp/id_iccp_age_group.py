from policyengine_us.model_api import *


class IDICCPAgeGroup(Enum):
    INFANT = "0-23 months"
    TODDLER = "24-35 months"
    PRESCHOOL = "36-59 months"
    SCHOOL_AGE = "5-12 years"


class id_iccp_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = IDICCPAgeGroup
    default_value = IDICCPAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    label = "Idaho Child Care Program age group"
    defined_for = StateCode.ID
    reference = "https://publicdocuments.dhw.idaho.gov/WebLink/DocView.aspx?dbid=0&id=19508&repo=PUBLIC-DOCUMENTS#page=1"

    def formula(person, period, parameters):
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        return parameters(period).gov.states.id.dhw.iccp.age_group.months.calc(
            age_months
        )
