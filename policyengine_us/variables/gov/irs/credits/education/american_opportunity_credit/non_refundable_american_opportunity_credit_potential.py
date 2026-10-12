from policyengine_us.model_api import *


class non_refundable_american_opportunity_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Potential value of the Non-refundable American Opportunity Credit"
    unit = USD
    documentation = (
        "Value of the non-refundable portion of the American Opportunity Credit"
    )
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"

    adds = ["american_opportunity_credit"]
    subtracts = ["refundable_american_opportunity_credit"]
