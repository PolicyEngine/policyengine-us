from policyengine_us.model_api import *


class ca_calworks_child_care_child_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the California CalWORKs Child Care based on age"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=11323.2",
        "https://www.cdss.ca.gov/ord/entres/getinfo/pdf/14EAS.pdf#page=34",
        "https://www.cdss.ca.gov/ord/entres/getinfo/pdf/4EAS.pdf#page=43",
        "https://www.cdss.ca.gov/ord/entres/getinfo/pdf/4EAS.pdf#page=44",
        "https://cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/CCBs/2025/CCB_25-15.pdf#page=6",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.child_care.eligibility
        age = person("age", period)
        is_disabled = person("is_disabled", period)
        # WIC 11323.2(a)(1)(A): paid childcare for a child 12 years of age or
        # under, a child needing care due to a disability, or a child under
        # court supervision.
        ordinary_age_eligible = age < p.age_threshold
        court_supervision = person("is_under_court_supervision", period)
        # MPP 47-201.2 limits the disabled and court-supervision routes to the
        # MPP 42-101 age: under 18, with an extension for 18-year-old students.
        under_extended_age = age < p.disabled_age_threshold
        student_age = age < p.student_age_threshold
        # is_in_k12_school is imputed only through age 17, so an 18-year-old
        # still in high school or vocational training is captured via
        # is_in_secondary_school ("or equivalent training"); enrollment
        # proxies the expected completion before 19.
        in_secondary_school = person("is_in_secondary_school", period)
        high_school_student = in_secondary_school | person("is_in_k12_school", period)
        full_time_student = in_secondary_school | person("is_full_time_student", period)
        # MPP 42-101.4-.6: a disabled 18-year-old who attends any school
        # full-time.
        disabled_age_eligible = under_extended_age | (student_age & full_time_student)
        # MPP 42-101.2: any other 18-year-old must be a full-time high school
        # or vocational student.
        court_age_eligible = under_extended_age | (
            student_age & high_school_student & full_time_student
        )
        return (
            ordinary_age_eligible
            | (is_disabled & disabled_age_eligible)
            | (court_supervision & court_age_eligible)
        )
