from openfisca_us.model_api import *


class snap_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP dependent care deduction"
    unit = "currency-USD"
    documentation = "Deduction from SNAP gross income for dependent care"
    definition_period = YEAR
    reference = "United States Code, Title 7, Section 2014(e)(3)"
