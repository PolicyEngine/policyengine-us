from policyengine_us.model_api import *


class medicaid_ltss_received_disability_payments_before_age_65(Variable):
    value_type = bool
    entity = Person
    label = "Received qualifying disability payments before age 65"
    definition_period = ETERNITY
    default_value = False
    documentation = (
        "Whether this person received SSI as a disabled individual, or "
        "disability payments under a former State plan, for the month "
        "before reaching age 65. This historical receipt fact preserves "
        "eligibility for the impairment-related work expense exclusion "
        "after age 65 under 20 CFR 416.1112(c)(6); it does not assert "
        "current disability or that any particular expense qualifies."
    )
    reference = "https://www.ssa.gov/OP_Home/cfr20/416/416-1112.htm"
