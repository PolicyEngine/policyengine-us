from policyengine_us.model_api import *


class takes_up_nm_premium_assistance_if_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether an eligible tax unit takes up New Mexico Premium Assistance"
    definition_period = YEAR
    # Take-up is assigned during microdata construction, not simulation time,
    # mirroring takes_up_aca_if_eligible.
    default_value = True
