from policyengine_us.model_api import *


class ca_sf_caap_is_recipient(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Current recipient of San Francisco County CAAP"
    definition_period = YEAR
    defined_for = "in_san_francisco"
    # Only current recipients get the earned income disregard; new applicants
    # do not. We default to applicant (no disregard).
    default_value = False
    reference = (
        # SEC. 20.7-21(j) limits the earned income disregard to recipients.
        "https://codelibrary.amlegal.com/codes/san_francisco/latest/sf_admin/0-0-0-65352"
    )
