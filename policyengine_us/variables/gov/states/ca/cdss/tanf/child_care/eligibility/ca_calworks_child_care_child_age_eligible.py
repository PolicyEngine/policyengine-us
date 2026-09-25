from policyengine_us.model_api import *


class ca_calworks_child_care_child_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the California CalWORKs Child Care based on age"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260AB119",
        "https://www.cdss.ca.gov/ord/entres/getinfo/pdf/14EAS.pdf#page=34",
        "https://www.cdss.ca.gov/ord/entres/getinfo/pdf/4EAS.pdf#page=43",
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
        # MPP 42-101 age: under 18, or 18 and a full-time high school student
        # expected to finish before 19. is_in_k12_school is imputed only
        # through age 17, so an 18-year-old still in high school is captured
        # via is_in_secondary_school; enrollment proxies the expected
        # completion.
        in_secondary_school = person("is_in_secondary_school", period)
        high_school_student = in_secondary_school | person("is_in_k12_school", period)
        full_time_student = in_secondary_school | person("is_full_time_student", period)
        student_age_eligible = (
            (age < p.disabled_age_threshold + 1)
            & high_school_student
            & full_time_student
        )
        extended_age_eligible = (age < p.disabled_age_threshold) | student_age_eligible
        extended_status = is_disabled | court_supervision
        return ordinary_age_eligible | (extended_status & extended_age_eligible)
