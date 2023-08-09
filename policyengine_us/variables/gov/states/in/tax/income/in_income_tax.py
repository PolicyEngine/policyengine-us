from policyengine_us.model_api import *


class in_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana income tax"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/6"

    adds = ["in_agi_tax", "in_other_taxes"]
