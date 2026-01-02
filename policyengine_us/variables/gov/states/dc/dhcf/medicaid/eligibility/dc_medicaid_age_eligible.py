from policyengine_us.model_api import *


class dc_medicaid_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets DC Medicaid age eligibility"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = [
        "https://dhcf.dc.gov/alliance",
        "https://dhcf.dc.gov/sites/default/files/dc/sites/dhcf/publication/attachments/Alliance%20and%20ICP%20Program%20Changes%20Resource%20Document.pdf",
    ]

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhcf.medicaid.eligibility
        age = person("age", period)
        is_pregnant = person("is_pregnant", period)

        # Check if person is currently enrolled (grandfathered for age only)
        is_currently_enrolled = person("dc_medicaid_enrolled", period)

        # New applicants over max age are not eligible starting 10/1/2025
        # Exception for pregnant women of any age
        # People over max_age can stay enrolled if already in the program
        # but new applicants over max_age cannot enroll
        # When max_age_new_applicants is infinity (before 10/1/2025),
        # the age <= max_age_new_applicants check will always pass
        return (
            (age <= p.max_age_new_applicants)
            | is_pregnant
            | (is_currently_enrolled & (age > p.max_age_new_applicants))
        )
