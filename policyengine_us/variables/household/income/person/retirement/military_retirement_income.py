from policyengine_us.model_api import *


class military_retirement_income(Variable):
    value_type = float
    entity = Person
    label = "Military retirement income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Total military retirement income, combining military retirement pay "
        "and military retirement survivor benefit payments."
    )
    reference = (
        "https://militarypay.defense.gov/Pay/Retirement/",
        "https://www.irs.gov/pub/irs-prior/p525--2024.pdf#page=16",
    )
    adds = ["military_retirement_pay", "military_retirement_pay_survivors"]
