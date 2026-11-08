from policyengine_us.model_api import *


class survivor_benefits(Variable):
    value_type = float
    entity = Person
    label = "survivor benefits"
    documentation = (
        "Survivor benefits other than Social Security survivor benefits. VA "
        "dependency and indemnity compensation goes in veterans_benefits, and "
        "Railroad Retirement Board survivor annuities in railroad_benefits."
    )
    unit = USD
    definition_period = YEAR
