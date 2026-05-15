from policyengine_us.model_api import *


class al_ccsp_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in Alabama CCSP"
    defined_for = StateCode.AL
    reference = (
        "Alabama CCDF State Plan 2025-2027, Section 2.2.4",
        "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=39",
    )
