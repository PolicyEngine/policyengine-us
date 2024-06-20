from policyengine_us.model_api import *


class estate_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Estate tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/2010"

    adds = [
        "estate_credit_basic_exclusion_amount",
        "estate_credit_deceased_spousal_unused_exclusion_amount",
    ]
