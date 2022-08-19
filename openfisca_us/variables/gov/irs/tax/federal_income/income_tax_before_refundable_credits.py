from openfisca_us.model_api import *


class income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Income tax before refundable credits"
    documentation = "Income tax liability (including othertaxes) after non-refundable credits are used, but before refundable credits are applied"

    def formula(tax_unit, period, parameters):
        income_tax_bc = tax_unit("income_tax_before_credits", period)
        capped_credits = tax_unit(
            "income_tax_capped_non_refundable_credits", period
        )
        taxes_net_nonrefundable_credits = income_tax_bc - capped_credits
        OTHER_TAXES = [
            "net_investment_income_tax",
            "recapture_of_investment_credit",
            "unreported_payroll_tax",
            "qualified_retirement_penalty",
        ]
        other_taxes = add(tax_unit, period, OTHER_TAXES)
        return taxes_net_nonrefundable_credits + other_taxes
