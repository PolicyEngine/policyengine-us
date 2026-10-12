from policyengine_us.model_api import *


class TNCCAPAgeCategory(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_IN = "School age, school in session"
    SCHOOL_OUT = "School age, school out of session"


class tn_ccap_age_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = TNCCAPAgeCategory
    default_value = TNCCAPAgeCategory.PRESCHOOL
    definition_period = MONTH
    label = "Tennessee CCAP child age category"
    defined_for = StateCode.TN
    reference = (
        "https://www.tn.gov/content/dam/tn/human-services/documents/Reimbursement_Rate_Chart_1.1.26.pdf",
        "https://www.tn.gov/content/dam/tn/human-services/documents/Current%20state%20rate%20and%20QRIS%20bonus%20table.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tn.dhs.ccap.age_category
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        is_in_school = person("is_in_k12_school", period.this_year)
        # School-age children default to the school-in-session rate; the
        # school-out-of-session rate is not modeled because there is no monthly
        # school-calendar input (scope decision: default School In).
        return select(
            [
                age_months < p.infant_max_months,
                age_months < p.toddler_max_months,
                ~is_in_school,
            ],
            [
                TNCCAPAgeCategory.INFANT,
                TNCCAPAgeCategory.TODDLER,
                TNCCAPAgeCategory.PRESCHOOL,
            ],
            default=TNCCAPAgeCategory.SCHOOL_IN,
        )
