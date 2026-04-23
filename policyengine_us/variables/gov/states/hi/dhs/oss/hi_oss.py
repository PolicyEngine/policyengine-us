from policyengine_us.model_api import *


class hi_oss(Variable):
    value_type = float
    entity = Person
    label = "Hawaii Optional State Supplementation"
    unit = USD
    definition_period = MONTH
    defined_for = "hi_oss_eligible"
    reference = (
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415200SF",
        "https://secure.ssa.gov/POMS.NSF/lnx/0501415057",
    )

    def formula(person, period, parameters):
        # Per POMS SI 02005.001: when federal SSI is payable, the
        # full state supplement applies. When countable income
        # exceeds the FBR, the excess reduces the supplement
        # dollar-for-dollar ("state supplement only" case).
        payment_standard = person("hi_oss_payment_amount", period)
        uncapped_ssi = person("uncapped_ssi", period)
        income_excess = max_(0, -uncapped_ssi)
        return max_(0, payment_standard - income_excess)
