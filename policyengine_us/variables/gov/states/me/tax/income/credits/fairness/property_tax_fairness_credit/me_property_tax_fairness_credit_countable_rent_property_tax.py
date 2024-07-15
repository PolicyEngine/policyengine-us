from policyengine_us.model_api import *


class me_property_tax_fairness_credit_countable_rent_property_tax(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Countable rent and property tax for Maine property tax fairness credit"
    definition_period = YEAR
    defined_for = StateCode.ME

    adds = [
        "me_property_tax_fairness_credit_countable_rent",
        "real_estate_taxes",
    ]
