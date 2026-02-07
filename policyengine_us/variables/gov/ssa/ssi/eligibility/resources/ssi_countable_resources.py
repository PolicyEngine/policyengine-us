from policyengine_us.model_api import *


class ssi_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "SSI countable resources"
    documentation = (
        "Countable resources for SSI eligibility. Includes liquid assets "
        "(bank accounts, stocks, bonds) but excludes home, one vehicle, "
        "household goods, and retirement accounts per SSI rules."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ssa.gov/ssi/spotlights/spot-resources.htm",
        "https://www.law.cornell.edu/uscode/text/42/1382b",
    )

    adds = "gov.ssa.ssi.eligibility.resources.countable"
