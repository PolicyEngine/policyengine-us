from openfisca_us import *


class ut_subtractions_from_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "UT subtractions from income"
    unit = USD
    documentation = "Description"
    definition_period = YEAR
