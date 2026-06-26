from policyengine_us.model_api import *


class ny_yonkers_nonresident_earnings(Variable):
    value_type = float
    entity = Person
    label = "Yonkers-source wages of a nonresident"
    unit = USD
    documentation = (
        "Wages sourced to Yonkers for a nonresident worker, used for the "
        "Yonkers nonresident earnings tax. Provided as an input."
    )
    definition_period = YEAR
