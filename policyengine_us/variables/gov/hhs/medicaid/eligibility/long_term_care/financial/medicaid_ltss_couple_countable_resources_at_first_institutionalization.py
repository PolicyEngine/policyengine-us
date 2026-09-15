from policyengine_us.model_api import *


class medicaid_ltss_couple_countable_resources_at_first_institutionalization(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS couple countable resources at first institutionalization"
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Trusted historical snapshot of the couple's total countable "
        "resources at the beginning of the first continuous period of "
        "institutionalization. The same snapshot should be supplied in each "
        "modeled month. The model does not reconstruct or adjudicate the "
        "snapshot."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396r-5"
