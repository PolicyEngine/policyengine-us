from openfisca_us.model_api import *


class snap_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "SNAP unearned income"
    documentation = "Unearned income for calculating the SNAP benefit"
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9#b_2"
    unit = USD

    formula = sum_of_variables("gov.usda.snap.income.sources.unearned")
