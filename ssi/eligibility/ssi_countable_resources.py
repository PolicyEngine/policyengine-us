from openfisca_us.model_api import *


class ssi_countable_resources(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income countable resources"
    label = "SSI countable resources"
    unit = USD
    quantity_type = STOCK
    reference = "https://www.law.cornell.edu/uscode/text/42/1382b#a"
