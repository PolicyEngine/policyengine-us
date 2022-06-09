from openfisca_us.model_api import *


class partnership_s_corp_income(Variable):
    value_type = float
    entity = Person
    label = "Partnership/S-corp income"
    unit = USD
    definition_period = YEAR
