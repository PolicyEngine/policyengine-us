from policyengine_us.model_api import *


class hi_total_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii total itemized deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32"  # total itemized deduction worksheet
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    adds = "gov.states.hi.tax.income.deductions.itemized.sources"
