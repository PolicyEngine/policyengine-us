from policyengine_us.model_api import *


class in_ccdf_has_active_under_18_award(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Has an active Indiana CCDF award determined before age 18"
    defined_for = StateCode.IN
    documentation = (
        "Whether this child is continuing an active CCDF award for documented "
        "special needs or court-ordered supervision whose most recent application "
        "or reapplication was approved before age 18. Defaults to true for a "
        "child with documented special needs or under court-ordered supervision "
        "and can be overridden per person. Do not set this from another "
        "household member's enrollment or for a new application at age 18."
    )
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=12"
    )

    def formula(person, period, parameters):
        # NOTE: default only. A qualifying child already in care is normally
        # continuing an award approved before age 18 (Section 1.6); set this
        # input to false explicitly for a new application at age 18.
        return person("is_disabled", period.this_year) | person(
            "is_under_court_supervision", period.this_year
        )
