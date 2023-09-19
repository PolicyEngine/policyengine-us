from policyengine_us.model_api import *


class hi_reduced_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii reduced itemized deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15",
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=19",
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32",  # total itemized deduction worksheet
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized
        p_deductions = parameters(period).gov.irs.deductions

        return
