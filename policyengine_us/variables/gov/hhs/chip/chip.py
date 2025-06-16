from policyengine_us.model_api import *


class chip(Variable):
    value_type = float
    entity = Person
    label = "CHIP"
    unit = USD
    definition_period = YEAR
    reference = "https://www.macpac.gov/publication/chip-spending-by-state/"
    defined_for = "is_chip_eligible"
    adds = ["per_capita_chip"]
