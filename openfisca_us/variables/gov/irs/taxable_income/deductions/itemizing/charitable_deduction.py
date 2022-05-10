from openfisca_us.model_api import *


class charitable_deduction(Variable):
    value_type = float
    entity = Person
    label = "Charitable deduction"
    unit = USD
    documentation = "Deduction from taxable income for charitable donations."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170"

    def formula(tax_unit, period, parameters):
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
        non_cash_donations = add(
            tax_unit, period, ["charitable_non_cash_donations"]
        )
        positive_agi = tax_unit("positive_agi", period)
        deduction = parameters(period).irs.deductions.itemized.charity.ceiling
        capped_non_cash_donations = min_(
            non_cash_donations, deduction.ceiling.non_cash
        )
        return min_(capped_non_cash_donations, deduction.ceiling.all)
