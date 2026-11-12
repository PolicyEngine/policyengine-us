from policyengine_us.model_api import *


class takes_up_csfp_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Takes up the Commodity Supplemental Food Program if eligible"
    documentation = (
        "Whether this person receives CSFP when eligible. Set this annual input "
        "during data construction or in a household calculation. It defaults "
        "to false; setting it to true pays the modeled annual amount when "
        "eligible. The input does not determine eligibility or enforce the "
        "caseload limits in 7 CFR 247.11."
    )
    reference = "https://www.govinfo.gov/content/pkg/CFR-2025-title7-vol4/pdf/CFR-2025-title7-vol4-sec247-10.pdf"
    definition_period = YEAR
    default_value = False
