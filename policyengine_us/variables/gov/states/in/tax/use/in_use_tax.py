from policyengine_us.model_api import *


class in_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana use tax"
    unit = USD
    definition_period = YEAR
    reference = "https://iga.in.gov/laws/2021/ic/titles/6#6-2.5-3"
    defined_for = StateCode.IN
