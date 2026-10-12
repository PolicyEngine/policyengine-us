from policyengine_us.model_api import *


class wi_cts_additional_fraction_disregard(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS additional one-third earnings disregard applies"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
