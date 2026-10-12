from policyengine_us.model_api import *


class wi_cts_additional_flat_disregard(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS additional 30 dollar earnings disregard applies"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
