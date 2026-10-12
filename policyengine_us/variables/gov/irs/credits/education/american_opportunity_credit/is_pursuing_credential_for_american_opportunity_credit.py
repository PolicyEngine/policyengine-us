from policyengine_us.model_api import *


class is_pursuing_credential_for_american_opportunity_credit(Variable):
    value_type = bool
    entity = Person
    label = "Pursuing a credential for the American Opportunity Credit"
    documentation = "Whether the student is pursuing a degree, certificate, or other recognized educational credential for American Opportunity Credit purposes."
    definition_period = YEAR
    reference = [
        "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A",
        "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title20-section1091",
    ]
