from policyengine_us.model_api import *


class chip(Variable):
    value_type = float
    entity = Person
    label = "CHIP"
    unit = USD
    definition_period = YEAR
    reference = "https://www.macpac.gov/publication/chip-spending-by-state/"
    documentation = (
        "Annual net CHIP benefit value for an enrolled person. This variable "
        "is gated by `chip_enrolled`, so it respects both eligibility and "
        "take-up. Use `chip_gross` for the eligibility-gated gross service "
        "value concept."
    )
    defined_for = "chip_enrolled"
    adds = ["per_capita_chip"]
