from policyengine_us.model_api import *


class il_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois LIHEAP total benefit"
    unit = USD
    definition_period = YEAR
    defined_for = "il_liheap_eligible"
    reference = "https://dceo.illinois.gov/communityservices/utilitybillassistance.html"

    adds = ["il_liheap_base_payment", "il_liheap_crisis_assistance_amount"]
