from policyengine_us.model_api import *


class al_ccsp_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    # Distinguishes new applicants, who face the initial limit, from continuing
    # recipients, who face the higher continuing limit (§2.5.2(c)(iii)); both
    # limits live in gov.states.al.dhr.ccsp.income.limit. Defaults to False,
    # so the model treats every household as a new applicant unless the user
    # sets this input.
    label = "Whether the family is currently enrolled in Alabama CCSP"
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=39"
