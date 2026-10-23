from policyengine_us.model_api import *


class wi_cts_received_recently(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS received in one of the previous four months"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=31"
