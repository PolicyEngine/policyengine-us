from policyengine_us.model_api import *


class nj_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey AGI subtractions"
    unit = USD
    documentation = "Subtractions from NJ AGI over federal AGI."
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/"
    adds = ["taxable_social_security"]
