from openfisca_us.model_api import *


class snap_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "SNAP gross income"
    documentation = "Gross income for calculating SNAP eligibility"
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#d"
    unit = USD

    formula = sum_of_variables(["snap_earned_income", "snap_unearned_income"])
