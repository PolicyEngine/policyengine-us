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
        return sum(
            [
                spm_unit(variable, period)
                for variable in [
                    "snap_standard_deduction",
                    "snap_earnings_deduction",
                    "snap_dependent_care_deduction",
                    "snap_child_support_deduction",
                    "snap_medical_expense_deduction",
                    "snap_shelter_deduction",
                ]
            ]
        )
