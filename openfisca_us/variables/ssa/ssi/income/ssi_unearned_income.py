from openfisca_us.model_api import *


class ssi_unearned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income unearned income"
    label = "SSI unearned income"
    unit = USD
