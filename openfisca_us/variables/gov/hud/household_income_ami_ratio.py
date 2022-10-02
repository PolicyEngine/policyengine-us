from openfisca_us.model_api import *


class household_income_ami_ratio(Variable):
    value_type = float
    entity = Household
    label = "Ratio of household income to area median income"
    definition_period = YEAR
