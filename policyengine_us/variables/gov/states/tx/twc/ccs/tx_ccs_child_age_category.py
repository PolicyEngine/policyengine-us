from policyengine_us.model_api import *


class TexasCCSChildAgeCategory(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class tx_ccs_child_age_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = TexasCCSChildAgeCategory
    default_value = TexasCCSChildAgeCategory.INFANT
    definition_period = MONTH
    defined_for = StateCode.TX
    label = "Texas Child Care Services (CCS) child age category"
    reference = (
        "https://regulations.justia.com/states/texas/title-40/part-20/chapter-809/subchapter-b/section-809-20/",
        "https://www.twc.texas.gov/programs/child-care-services",
    )

    def formula(person, period, parameters):
        # Get child's age in years (convert to months for infant threshold)
        age_years = person("age", period.this_year)
        age_months = age_years * MONTHS_IN_YEAR
        p = parameters(period).gov.states.tx.twc.ccs.age_threshold
        return select(
            [
                age_months < p.infant,  # Under 18 months = Infant
                age_years < p.toddler,  # Under 3 years = Toddler
                age_years < p.school_age,  # Under 6 years = Preschool
            ],
            [
                TexasCCSChildAgeCategory.INFANT,
                TexasCCSChildAgeCategory.TODDLER,
                TexasCCSChildAgeCategory.PRESCHOOL,
            ],
            default=TexasCCSChildAgeCategory.SCHOOL_AGE,
        )
