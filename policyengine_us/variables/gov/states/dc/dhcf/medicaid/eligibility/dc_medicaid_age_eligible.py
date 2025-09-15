from policyengine_us.model_api import *


class dc_medicaid_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "DC Medicaid age eligible"
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

        # New applicants 26+ are not eligible starting 10/1/2025
        # Exception for pregnant women of any age
        max_age_new_applicants = p.max_age_new_applicants

        # If max_age is set to a finite value (after 10/1/2025), apply the restriction
        import numpy as np

        if not np.isinf(max_age_new_applicants):
            # People over 26 can stay enrolled if already in the program
            # but new applicants over 26 cannot enroll
            age_eligible = (
                (age <= max_age_new_applicants)
                | is_pregnant
                | (
                    is_currently_enrolled & (age >= 26)
                )  # Only grandfather those over 26
            )
        else:
            # Before 10/1/2025, no age restriction (inf means no limit)
            age_eligible = True

        return age_eligible
