from policyengine_us.model_api import *


class nm_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico income deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    adds = [
        "standard_deduction",
        "nm_itemized_deductions",
        "nm_deduction_for_certain_dependents",
        "nm_medical_care_expense_deduction",
        "nm_net_capital_gains_deduction",
    ]
