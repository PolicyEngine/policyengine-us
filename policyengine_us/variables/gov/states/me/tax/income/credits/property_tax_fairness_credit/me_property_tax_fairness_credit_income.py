from policyengine_us.model_api import *


class me_property_tax_fairness_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine property tax fairness credit total income"
    definition_period = YEAR
    reference = "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html" # 1. D.
    defined_for = StateCode.ME

    adds = ["adjusted_gross_income", "social_security_benefits", "tax_exempt_interest_income"]