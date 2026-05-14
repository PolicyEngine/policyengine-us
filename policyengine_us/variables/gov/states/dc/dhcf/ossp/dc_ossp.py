from policyengine_us.model_api import *


class dc_ossp(Variable):
    value_type = float
    entity = Person
    label = "DC Optional State Supplemental Payment"
    unit = USD
    definition_period = MONTH
    defined_for = "dc_ossp_eligible"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.49",
        "https://www.ssa.gov/pubs/EN-05-11162.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per POMS SI 02005.001: when federal SSI is payable, the
        # full state supplement applies. When countable income
        # exceeds the FBR, the excess reduces the supplement
        # dollar-for-dollar ("state supplement only" case).
        payment_standard = person("dc_ossp_payment_amount", period)
        uncapped_ssi = person("uncapped_ssi", period)
        income_excess = max_(0, -uncapped_ssi)
        return max_(0, payment_standard - income_excess)
