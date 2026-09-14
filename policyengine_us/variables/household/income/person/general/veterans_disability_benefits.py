from policyengine_us.model_api import *


class veterans_disability_benefits(Variable):
    value_type = float
    entity = Person
    label = "Veterans disability benefits included in total veterans benefits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/eec-policy-advisory-field-operations-7-child-care-financial-assistance-updated-policy-guidance/download#page=3"
