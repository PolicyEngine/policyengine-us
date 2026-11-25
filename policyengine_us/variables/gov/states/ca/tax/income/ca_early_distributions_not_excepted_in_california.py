from policyengine_us.model_api import *


class ca_early_distributions_not_excepted_in_california(Variable):
    value_type = float
    entity = Person
    label = "Early distributions excepted federally but not in California"
    documentation = (
        "Early distributions that meet a federal exception California has "
        "not adopted (for example 529-to-Roth IRA rollovers, IRA-to-HSA "
        "rollovers and qualified recovery assistance distributions), and "
        "that are includible in California income."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2025/2025-3805p-instructions.html"
    defined_for = StateCode.CA
