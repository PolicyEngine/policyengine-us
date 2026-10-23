from policyengine_us.model_api import *


class mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "Mortgage interest"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Home mortgage interest and deductible points, before the federal "
        "acquisition-debt caps."
    )

    adds = ["non_deductible_mortgage_interest", "deductible_mortgage_interest"]
