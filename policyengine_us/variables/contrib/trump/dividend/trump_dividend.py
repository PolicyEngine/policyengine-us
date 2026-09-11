from policyengine_us.model_api import *


class trump_dividend(Variable):
    value_type = float
    entity = Person
    label = "Trump dividend"
    unit = USD
    documentation = (
        "Trump dividend payment for this person. By design the payment "
        "is non-taxable (excluded from adjusted gross income and MAGI "
        "bases) and does not enter SNAP or SSI countable income; it "
        "flows only into the benefit aggregates, matching the "
        "basic_income default non-taxable treatment."
    )
    definition_period = YEAR
    defined_for = "trump_dividend_eligible"

    adds = ["gov.contrib.trump.dividend.amount"]
