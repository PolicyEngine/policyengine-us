from policyengine_us.model_api import *


class hi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii additions to federal adjusted gross income"
    reference = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=11"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
