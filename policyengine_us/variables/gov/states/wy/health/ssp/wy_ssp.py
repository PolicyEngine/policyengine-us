from policyengine_us.model_api import *


class wy_ssp(Variable):
    value_type = float
    entity = Person
    label = "Wyoming State Supplemental Payment"
    definition_period = MONTH
    unit = USD
    defined_for = "wy_ssp_eligible"
    reference = (
        "https://ecom.wyo.gov/m1800-other-programs/m1804-state-supplemental-payments"
    )
    adds = ["gov.states.wy.health.ssp.amount"]
