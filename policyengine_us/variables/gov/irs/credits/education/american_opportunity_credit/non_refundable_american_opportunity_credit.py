from policyengine_us.model_api import *


class non_refundable_american_opportunity_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Non-refundable American Opportunity Credit"
    unit = USD
    documentation = "Value of the non-refundable portion of the American Opportunity Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#i"

    adds = ["american_opportunity_credit"]
    subtracts = ["refundable_american_opportunity_credit"]


c87668 = variable_alias("c87668", non_refundable_american_opportunity_credit)
