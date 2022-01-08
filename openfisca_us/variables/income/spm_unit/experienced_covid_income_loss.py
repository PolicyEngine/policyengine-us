from openfisca_us.model_api import *


class experienced_covid_income_loss(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Experienced Covid income loss"
    documentation = "Whether the SPM unit experienced a loss of income due to COVID-19 since February 2020"
    definition_period = YEAR
