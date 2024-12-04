from policyengine_us.model_api import *


class chapter_7_bankruptcy_debt_payment_deductions(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Debt payment deduction"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=7"

    def formula(spm_unit, period, parameters):
        housing_expense = add(spm_unit,period,["housing_cost"])
        vehicle_mortgage_expense = add(spm_unit,period,["vehicle_mortgage_expense"])
        total = housing_expense + vehicle_mortgage_expense
        return total/MONTHS_IN_YEAR
    