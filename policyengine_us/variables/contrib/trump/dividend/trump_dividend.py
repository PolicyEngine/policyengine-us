from policyengine_us.model_api import *


class trump_dividend(Variable):
    value_type = float
    entity = Person
    label = "Trump dividend"
    unit = USD
    documentation = "Trump dividend payment for this person."
    definition_period = YEAR
    defined_for = "trump_dividend_eligible"

    adds = ["gov.contrib.trump.dividend.amount"]
