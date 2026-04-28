from policyengine_us.model_api import *


class health_insurance_premium_residual(Variable):
    value_type = float
    entity = Person
    label = "Residual health insurance premiums"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Residual person-level health insurance premiums after subtracting "
        "baseline modeled premium components, such as Marketplace, CHIP, "
        "Medicaid, and Medicare Part B premiums. This is an accounting "
        "residual imputed by microdata pipelines, not a directly observed "
        "coverage category."
    )
