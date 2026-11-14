from policyengine_us.model_api import *


class sd_cca_special_needs_rate_approved(Variable):
    value_type = bool
    entity = Person
    default_value = False
    definition_period = MONTH
    defined_for = StateCode.SD
    label = "South Dakota CCA special-needs reimbursement rate approved"
    documentation = "Records whether DSS approved enhanced reimbursement for the child after reviewing medical documentation and the provider's enhanced services. Subsidy Manual Section 19 requires this review separately from child eligibility."
    reference = "https://web.archive.org/web/20251031171652/https://dss.sd.gov/docs/childcare/assistance/Subsidy_Manual.pdf#page=39"
