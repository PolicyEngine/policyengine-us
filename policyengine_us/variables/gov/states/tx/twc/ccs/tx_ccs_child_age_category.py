from policyengine_us.model_api import *


class TexasCCSChildAgeCategory(Enum):
    # Pre-2025-10-01 categories (4 groups)
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"
    # Expanded categories per 26 TAC §746.1601 (8 groups)
    AGE_0_11_MONTHS = "0-11 months"
    AGE_12_17_MONTHS = "12-17 months"
    AGE_18_23_MONTHS = "18-23 months"
    AGE_2_YEARS = "2 years"
    AGE_3_YEARS = "3 years"
    AGE_4_YEARS = "4 years"
    AGE_5_YEARS = "5 years"
    AGE_6_13_YEARS = "6-13 years"


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
        "https://www.law.cornell.edu/regulations/texas/26-Tex-Admin-Code-SS-746-1601",
    )

    def formula(person, period, parameters):
        age_years = person("age", period.this_year)
        age_months = age_years * MONTHS_IN_YEAR
        p = parameters(period).gov.states.tx.twc.ccs

        uses_expanded = p.payment.uses_expanded_age_groups

        if uses_expanded:
            p_exp = p.expanded_age_threshold
            return select(
                [
                    age_months < p_exp.age_0_11_months,
                    age_months < p_exp.age_12_17_months,
                    age_months < p_exp.age_18_23_months,
                    age_months < p_exp.age_2_years,
                    age_months < p_exp.age_3_years,
                    age_months < p_exp.age_4_years,
                    age_months < p_exp.age_5_years,
                ],
                [
                    TexasCCSChildAgeCategory.AGE_0_11_MONTHS,
                    TexasCCSChildAgeCategory.AGE_12_17_MONTHS,
                    TexasCCSChildAgeCategory.AGE_18_23_MONTHS,
                    TexasCCSChildAgeCategory.AGE_2_YEARS,
                    TexasCCSChildAgeCategory.AGE_3_YEARS,
                    TexasCCSChildAgeCategory.AGE_4_YEARS,
                    TexasCCSChildAgeCategory.AGE_5_YEARS,
                ],
                default=TexasCCSChildAgeCategory.AGE_6_13_YEARS,
            )

        return select(
            [
                age_months < p.age_threshold.infant,
                age_years < p.age_threshold.toddler,
                age_years < p.age_threshold.school_age,
            ],
            [
                TexasCCSChildAgeCategory.INFANT,
                TexasCCSChildAgeCategory.TODDLER,
                TexasCCSChildAgeCategory.PRESCHOOL,
            ],
            default=TexasCCSChildAgeCategory.SCHOOL_AGE,
        )
