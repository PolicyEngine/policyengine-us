from openfisca_us.model_api import *


class ssi_unearned_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI unearned income (deemed from ineligible spouse)"
    unit = USD
    definition_period = YEAR

