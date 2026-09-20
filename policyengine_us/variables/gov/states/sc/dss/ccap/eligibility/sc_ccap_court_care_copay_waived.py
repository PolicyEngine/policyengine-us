from policyengine_us.model_api import *


class sc_ccap_court_care_copay_waived(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    defined_for = StateCode.SC
    label = "South Carolina CCAP court-care copayment waiver"
    documentation = "Whether the agency has approved the copayment waiver for this family based on court-supervised child care under manual section 2.4. The court-supervision flag alone does not identify which of the two waivers was authorized."
    reference = (
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=65"
    )
