from openfisca_us.model_api import *


class puerto_rico_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income from Puerto Rico"
    unit = USD
    documentation = "Income generated in Puerto Rico by any individual who is a bona fide resident."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/933"
