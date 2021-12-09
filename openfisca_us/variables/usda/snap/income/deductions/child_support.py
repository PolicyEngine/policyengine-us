from openfisca_us.model_api import *


class snap_child_support_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP child support payment deduction"
    unit = "currency-USD"
    documentation = (
        "Deduction from SNAP gross income for child support payments"
    )
    definition_period = YEAR
    reference = "United States Code, Title 7, Section 2014(e)(4)"
