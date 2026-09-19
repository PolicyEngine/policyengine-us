from policyengine_us.model_api import *


class medicaid_ltss_community_spouse_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS community spouse countable resources"
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Trusted current comprehensive LTSS countable resources allocated to "
        "the community spouse after applicable ownership and exclusion "
        "rules. Court orders, fair-hearing adjustments, and legal ownership "
        "determinations are not modeled."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396r-5"
