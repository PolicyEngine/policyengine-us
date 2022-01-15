from openfisca_us.model_api import *


class snap_medical_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP excess medical expense deduction"
    unit = USD
    documentation = (
        "Deduction from SNAP gross income for excess medical expenses"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_5"
