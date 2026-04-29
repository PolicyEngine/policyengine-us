from policyengine_us.model_api import *


class other_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Other health insurance premiums"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Person-level health insurance premiums not otherwise represented by "
        "modeled Marketplace, CHIP, Medicaid, or Medicare Part B premiums."
    )
