from policyengine_us.model_api import *


class loss_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Business and capital loss ALD"
    unit = USD
    documentation = (
        "Above-the-line deduction from gross income for business and capital losses."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/165",
        "https://www.law.cornell.edu/uscode/text/26/461#l",
        "https://www.law.cornell.edu/uscode/text/26/1211#b",
    )

    def formula(tax_unit, period, parameters):
        # Section 461(l) excess business loss limitation
        limited_business_loss = tax_unit("limited_business_loss", period)

        # Section 1211(b) allows capital losses to the extent of capital
        # gains, plus a net loss of up to $3,000.
        capital_losses_allowed_against_gains = tax_unit(
            "capital_losses_allowed_against_gains", period
        )
        limited_capital_loss = tax_unit("limited_capital_loss", period)

        return (
            limited_business_loss
            + capital_losses_allowed_against_gains
            + limited_capital_loss
        )
