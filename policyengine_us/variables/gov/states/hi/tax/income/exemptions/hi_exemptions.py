from policyengine_us.model_api import *


class hi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii exemptions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    adds = ["hi_dependent_exemptions", "hi_head_or_spouse_exemptions"]
