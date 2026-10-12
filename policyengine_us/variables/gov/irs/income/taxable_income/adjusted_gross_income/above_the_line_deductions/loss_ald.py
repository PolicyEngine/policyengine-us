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

    # Business losses allowed under section 461(l), plus capital losses
    # allowed under section 1211(b): to the extent of capital gains, and a net
    # loss of up to $3,000.
    adds = [
        "limited_business_loss",
        "capital_losses_allowed_against_gains",
        "limited_capital_loss",
    ]
