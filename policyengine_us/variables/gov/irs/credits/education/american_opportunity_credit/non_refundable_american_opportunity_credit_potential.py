from policyengine_us.model_api import *


class non_refundable_american_opportunity_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Potential value of the Non-refundable American Opportunity Credit"
    unit = USD
    documentation = "Value of the non-refundable portion of the American Opportunity Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#i"

    adds = ["american_opportunity_credit"]
    subtracts = ["refundable_american_opportunity_credit"]
