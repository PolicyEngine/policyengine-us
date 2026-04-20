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
        "https://secure.ssa.gov/poms.nsf/lnx/0501140000",  # POMS SI 01140.000 - Types of Countable Resources
    )

    adds = "gov.ssa.ssi.eligibility.resources.countable"
