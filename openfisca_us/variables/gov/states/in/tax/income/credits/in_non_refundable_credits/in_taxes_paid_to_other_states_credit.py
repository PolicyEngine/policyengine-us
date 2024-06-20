from openfisca_us.model_api import *


class in_taxes_paid_to_other_states_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN credit for taxes paid to other states"
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-3-3"
