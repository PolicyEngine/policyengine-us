from openfisca_us.model_api import *


class snap_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP income deductions"
    unit = "currency-USD"
    documentation = "Deductions made from gross income for SNAP benefits"
    definition_period = YEAR
    reference = "United States Code, Title 7, Section 2014(e)"

    def formula(spm_unit, period, parameters):
        snap_deductions = parameters(period).usda.snap.deductions
        return add(spm_unit, period, *snap_deductions.allowed)
