from policyengine_us.model_api import *


class sd_cca_reason_for_care_eligible(Variable):
    value_type = bool
    entity = Person
    label = "South Dakota CCA reason-for-care eligible"
    definition_period = MONTH
    defined_for = StateCode.SD
    reference = (
        "https://dss.sd.gov/docs/childcare/assistance/Subsidy_Manual.pdf#page=8",
        "https://sdlegislature.gov/Rules/Administrative/67:47:01:03",
    )

    def formula(person, period, parameters):
        # A child needs care when every caretaker is in an approved activity
        # or when the child receives or needs protective services
        # (ARSD 67:47:01:03), mirroring the federal
        # is_ccdf_reason_for_care_eligible pattern.
        parent_activity_eligible = person.spm_unit("sd_cca_activity_eligible", period)
        protective_services = person(
            "receives_or_needs_protective_services", period.this_year
        )
        return parent_activity_eligible | protective_services
