from policyengine_us.model_api import *


class unified_credit_against_estate_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Unified credit against estate tax"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/2010"

    adds = [
        "basic_exclusion_amount",
        "deceased_spousal_unused_exclusion_amount",
    ]
