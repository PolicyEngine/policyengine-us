from policyengine_us.model_api import *


class ma_pfml_received(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts paid family and medical leave benefits received"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=21"
