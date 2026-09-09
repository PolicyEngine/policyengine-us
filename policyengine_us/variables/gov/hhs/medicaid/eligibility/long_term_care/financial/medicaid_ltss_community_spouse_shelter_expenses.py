from policyengine_us.model_api import *


class medicaid_ltss_community_spouse_shelter_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS community spouse shelter expenses"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Trusted monthly shelter expenses of the community spouse that are "
        "allowable for the minimum monthly maintenance needs allowance. The "
        "model does not determine which housing or utility costs qualify."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396r-5"
