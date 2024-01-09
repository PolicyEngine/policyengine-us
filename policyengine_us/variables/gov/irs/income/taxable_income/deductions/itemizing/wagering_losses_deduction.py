from policyengine_us.model_api import *


class wagering_losses_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wagering losses deduction"
    unit = USD
    documentation = "Deduction from taxable income for gambling losses, capped at gambling winnings."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/165#d"

    def formula(tax_unit, period, parameters):
        gambling_losses = add(tax_unit, period, ["gambling_losses"])
        gambling_winnings = add(tax_unit, period, ["gambling_winnings"])
        return min_(gambling_losses, gambling_winnings)
