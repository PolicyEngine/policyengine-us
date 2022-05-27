from openfisca_us.model_api import *


class ssi_earned_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI earned income (deemed from ineligible spouse)"
    unit = USD
    definition_period = YEAR

