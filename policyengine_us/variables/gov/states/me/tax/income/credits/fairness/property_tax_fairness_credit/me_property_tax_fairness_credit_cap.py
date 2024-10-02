from policyengine_us.model_api import *


class me_property_tax_fairness_credit_cap(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine property tax fairness credit cap"
    definition_period = YEAR
    defined_for = StateCode.ME

    adds = [
        "me_property_tax_fairness_credit_base_cap",
        "me_property_tax_fairness_credit_veterans_cap",
    ]
