from policyengine_us.model_api import *


class ia_cca_court_ordered_care_approved(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    defined_for = StateCode.IA
    label = "Iowa HHS has approved court-ordered child care"
    documentation = "Whether Iowa HHS is providing child care for this child pursuant to a court order under 441 IAC 170.2(1)b(4). An order requiring care or general supervision alone does not establish departmental approval."
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=4",
        "https://hhs.iowa.gov/media/3816#page=47",
    )
