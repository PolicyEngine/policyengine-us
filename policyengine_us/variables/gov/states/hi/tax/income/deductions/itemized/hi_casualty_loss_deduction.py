from policyengine_us.model_api import *


class hi_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii casualty loss deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=18"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32"  # total itemized deduction worksheet
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p_deductions = parameters(period).gov.irs.deductions
        # 5. casualty_loss_deduction: worksheet A-5
        # Hawaii did not
        #     (1) limit the personal casualty loss deduction for property losses (not used in connection with a trade or business
        #       or transaction entered into for profit)
        #     (2) waive the requirement that casualty losses from qualified disasters exceed 10% of adjusted gross income
        #       to be deductible, and that such losses must exceed $500.
        casualty_loss = add(tax_unit, period, ["casualty_loss"])
        hi_agi = tax_unit("hi_agi", period)
        casualty_agi_amount = max_(
            0, p_deductions.itemized.casualty.floor * hi_agi
        )
        return max_(0, casualty_loss - casualty_agi_amount)
