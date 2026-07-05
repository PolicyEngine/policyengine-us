from policyengine_us.model_api import *


class basic_health_program_reference_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic Health Program reference premium"
    unit = USD
    definition_period = MONTH
    adds = [
        "basic_health_program_age_curve_amount_person",
        "basic_health_program_family_tier_amount",
    ]
