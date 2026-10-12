from policyengine_us.model_api import *


class SDCCAAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School age"


class sd_cca_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = SDCCAAgeGroup
    default_value = SDCCAAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    defined_for = StateCode.SD
    label = "South Dakota CCA rate-table age group"
    reference = (
        "https://dss.sd.gov/docs/childcare/assistance/CCA_Weekly_Reimbursement_Rates.pdf",
        "https://dss.sd.gov/docs/childcare/assistance/BEES_CCA_Policy_Manual.pdf#page=45",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sd.dss.cca.age_group
        # Infant is under 12 months, toddler 12 through 35 months, and preschool
        # 36 through 71 months. A child 60 through 71 months old who is enrolled
        # in school is classified as school age rather than preschool: the rate
        # table prints the 60-71-month preschool/school-age overlap, and BEES
        # Section 10.2.4 ties school-aged treatment to school attendance.
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        is_in_school = person("is_in_k12_school", period.this_year)
        school_age_by_enrollment = (
            age_months >= p.school_age_min_months
        ) & is_in_school
        return select(
            [
                age_months < p.infant_max_months,
                age_months < p.toddler_max_months,
                (age_months < p.preschool_max_months) & ~school_age_by_enrollment,
            ],
            [
                SDCCAAgeGroup.INFANT,
                SDCCAAgeGroup.TODDLER,
                SDCCAAgeGroup.PRESCHOOL,
            ],
            default=SDCCAAgeGroup.SCHOOL_AGE,
        )
