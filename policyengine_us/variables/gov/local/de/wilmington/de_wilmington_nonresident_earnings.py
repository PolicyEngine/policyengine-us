from policyengine_us.model_api import *


class de_wilmington_nonresident_earnings(Variable):
    value_type = float
    entity = Person
    label = "Wilmington-source earnings of a nonresident"
    unit = USD
    documentation = (
        "Earned income sourced to Wilmington for a nonresident worker, used "
        "for the Wilmington nonresident wage tax. Provided as an input."
    )
    definition_period = YEAR
