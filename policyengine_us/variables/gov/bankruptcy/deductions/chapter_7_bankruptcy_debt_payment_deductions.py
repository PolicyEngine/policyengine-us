from policyengine_us.model_api import *


class chapter_7_bankruptcy_debt_payment_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "Debt payment deductions"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=7"

    def formula(spm_unit, period, parameters):
        housing_expense = spm_unit("housing_cost", period)
        vehicle_mortgage_expense = add(
            spm_unit, period, ["vehicle_mortgage_expense"]
        )
        return housing_expense + vehicle_mortgage_expense
