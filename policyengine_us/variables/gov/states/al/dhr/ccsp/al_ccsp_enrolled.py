from policyengine_us.model_api import *


class al_ccsp_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    # Distinguishes new applicants (180% FPL initial cap) from continuing
    # recipients (200% FPL continuing cap, §2.5.2(c)(iii)). Defaults to
    # False, so every household is treated as a new applicant unless this
    # input is explicitly set.
    label = "Whether the family is currently enrolled in Alabama CCSP"
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=39"
