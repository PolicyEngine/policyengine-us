from openfisca_us.model_api import *


class medicaid_benefit_value(Variable):
    value_type = float
    entity = Person
    label = "Average Medicaid payment"
    unit = USD
    documentation = "Per-capita payment for this person's State."
    definition_period = YEAR
