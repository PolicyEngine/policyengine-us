from policyengine_us.model_api import *


class DCCCSPAgeCategory(Enum):
    INFANT_AND_TODDLER = "Infant and toddler (under 36 months)"
    PRESCHOOL = "Preschool (36-59 months)"
    SCHOOL_AGE = "School-age (60+ months)"


class dc_ccsp_age_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = DCCCSPAgeCategory
    default_value = DCCCSPAgeCategory.INFANT_AND_TODDLER
    definition_period = MONTH
    label = "DC Child Care Subsidy Program (CCSP) child age category"
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/Final%20Rulemaking%20for%20the%20Licensing%20of%20Child%20Development%20Facilities.pdf#page=172"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp.age_category
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        return p.months.calc(age_months)
