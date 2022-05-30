from openfisca_us.model_api import *


class ssi_earned_income_deemed_from_ineligible_parent(Variable):
    value_type = float
    entity = Person
    label = "SSI earned income (deemed from ineligible parent)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1165"

