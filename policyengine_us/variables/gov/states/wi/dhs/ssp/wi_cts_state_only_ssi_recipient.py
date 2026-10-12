from policyengine_us.model_api import *


class wi_cts_state_only_ssi_recipient(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS parent receives grandfathered state-only SSI"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
