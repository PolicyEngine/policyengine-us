from policyengine_us.model_api import *


class MassachusettsCCFAChildAgeCategory(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class ma_ccfa_child_age_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = MassachusettsCCFAChildAgeCategory
    default_value = MassachusettsCCFAChildAgeCategory.INFANT
    definition_period = MONTH
    defined_for = StateCode.MA
    label = "Massachusetts Child Care Financial Assistance (CCFA) child age category"
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/606-CMR-7-10",
        "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download",
    )

    def formula(person, period, parameters):
        # Get child's age in years (convert to months for thresholds)
        age_years = person("age", period.this_year)
        age_months = age_years * MONTHS_IN_YEAR

        # Get age threshold parameters
        p = parameters(period).gov.states.ma.eec.ccfa.age_threshold

        # Determine age category based on Massachusetts 606 CMR 7.10
        return select(
            [
                age_months <= p.infant,
                age_months <= p.toddler,
                age_years < p.school_age,
            ],
            [
                MassachusettsCCFAChildAgeCategory.INFANT,
                MassachusettsCCFAChildAgeCategory.TODDLER,
                MassachusettsCCFAChildAgeCategory.PRESCHOOL,
            ],
            default=MassachusettsCCFAChildAgeCategory.SCHOOL_AGE,
        )
