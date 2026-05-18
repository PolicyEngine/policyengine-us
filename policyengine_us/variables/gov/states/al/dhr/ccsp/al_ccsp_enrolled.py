from policyengine_us.model_api import *


class al_ccsp_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in Alabama CCSP"
    documentation = (
        "Distinguishes new applicants (180% FPL initial-eligibility cap) "
        "from continuing recipients (200% FPL cap). Defaults to False, so "
        "every microdata household is treated as a new applicant unless "
        "the user explicitly sets this input — the 200% FPL continuing "
        "branch is unreachable without it."
    )
    defined_for = StateCode.AL
    reference = (
        "Alabama CCDF State Plan 2025-2027, Section 2.5.5(c)(iii)",
        "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=39",
    )
