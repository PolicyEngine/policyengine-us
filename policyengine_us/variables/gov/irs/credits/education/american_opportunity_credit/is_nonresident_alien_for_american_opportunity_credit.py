from policyengine_us.model_api import *


class is_nonresident_alien_for_american_opportunity_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Nonresident alien for American Opportunity Credit"
    documentation = "Whether the taxpayer is a nonresident alien for American Opportunity Credit purposes and is not treated as a resident alien under section 6013(g) or 6013(h)."
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"
