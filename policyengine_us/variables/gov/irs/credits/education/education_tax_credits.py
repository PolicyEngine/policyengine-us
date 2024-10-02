from policyengine_us.model_api import *


class education_tax_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Education tax credits"
    documentation = (
        "Education tax credits non-refundable amount from Form 8863"
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25A"

    adds = [
        "non_refundable_american_opportunity_credit",
        "lifetime_learning_credit",
    ]
