from policyengine_us.model_api import *


class il_hbi_new_enrollment_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for new enrollment in Illinois Health Benefits for Immigrants"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = [
        "https://hfs.illinois.gov/medicalclients/healthbenefitsforimmigrants.html",
        "https://www.dhs.state.il.us/page.aspx?item=161600",
    ]
    documentation = """
    Whether a person is eligible to newly enroll in Illinois Health Benefits
    for Immigrants. This combines eligibility with whether new enrollment is
    currently open for their age group.

    - Children (All Kids): Open enrollment
    - Adults 42-64 (HBIA): New enrollment paused July 1, 2023
    - Seniors 65+ (HBIS): New enrollment paused November 6, 2023
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbi.eligibility

        # Must be eligible
        eligible = person("il_hbi_eligible", period)

        # Determine age group
        age = person("age", period)
        child_max_age = p.child_max_age
        adult_min_age = p.adult_min_age
        adult_max_age = p.adult_max_age
        senior_min_age = p.senior_min_age

        is_child = age <= child_max_age
        is_adult = (age >= adult_min_age) & (age <= adult_max_age)
        is_senior = age >= senior_min_age

        # Check if new enrollment is open for age group
        child_open = p.child_new_enrollment_open
        adult_open = p.adult_new_enrollment_open
        senior_open = p.senior_new_enrollment_open

        enrollment_open = (
            (is_child & child_open)
            | (is_adult & adult_open)
            | (is_senior & senior_open)
        )

        return eligible & enrollment_open
