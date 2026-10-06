from policyengine_us.model_api import *


class loss_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Business loss ALD"
    unit = USD
    documentation = (
        "Above-the-line deduction from gross income for business and capital losses."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/165",
        "https://www.law.cornell.edu/uscode/text/26/461#l",
        "https://www.law.cornell.edu/uscode/text/26/1211",
    )

    # Business losses allowed under section 461(l), plus capital losses
    # allowed under section 1211(b), each limited separately.
    adds = ["limited_business_loss", "limited_capital_loss"]
