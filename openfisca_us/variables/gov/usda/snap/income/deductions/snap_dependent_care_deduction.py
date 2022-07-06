from openfisca_us.model_api import *


class snap_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP dependent care deduction"
    unit = USD
    documentation = "Deduction from SNAP gross income for dependent care"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_3"

    formula = sum_of_variables(["childcare_expenses"])
