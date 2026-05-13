from policyengine_us.model_api import *


class VACCSPCareAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    TWO_YEAR_OLD = "2 year old"
    PRESCHOOL = "Pre-School"
    SCHOOL_AGE = "School Age"


class va_ccsp_care_age_group(Variable):
    value_type = Enum
    possible_values = VACCSPCareAgeGroup
    default_value = VACCSPCareAgeGroup.INFANT
    entity = Person
    definition_period = YEAR
    label = "Virginia CCSP care age group"
    defined_for = StateCode.VA
    reference = "https://www.childcare.virginia.gov/home/showpublisheddocument/66667/638981099706730000#page=203"

    def formula(person, period, parameters):
        age_months = person("age", period) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.va.dss.ccsp.maximum_reimbursement_rate
        return p.care_age_group.calc(age_months)
