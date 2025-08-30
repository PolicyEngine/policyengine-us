from policyengine_us.model_api import *


class il_liheap_crisis_assistance_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois LIHEAP crisis assistance amount"
    unit = USD
    definition_period = YEAR
    defined_for = "il_liheap_eligible_for_crisis_assistance"
    reference = "https://dceo.illinois.gov/communityservices/utilitybillassistance.html"

    adds = ["gov.states.il.dceo.liheap.payment.crisis_amount.max"]
