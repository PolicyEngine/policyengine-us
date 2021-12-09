from openfisca_us.model_api import *


class snap_medical_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP excess medical expense deduction"
    unit = "currency-USD"
    documentation = (
        "Deduction from SNAP gross income for excess medical expenses"
    )
    definition_period = YEAR
    reference = "United States Code, Title 7, Section 2014(e)(5)"
