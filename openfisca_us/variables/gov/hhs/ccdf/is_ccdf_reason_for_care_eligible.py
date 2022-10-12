from policyengine_us.model_api import *


class is_ccdf_reason_for_care_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether child qualifies for CCDF based on parents meeting activity test or that he/she receives or needs protective services"
    label = "Reason-for-care eligibility for CCDF"

    def formula(person, period):
        parent_meets_ccdf_activity_test = person.spm_unit(
            "meets_ccdf_activity_test", period
        )
        child_receives_or_needs_protective_services = person(
            "receives_or_needs_protective_services", period
        )
        return (
            parent_meets_ccdf_activity_test
            | child_receives_or_needs_protective_services
        )
