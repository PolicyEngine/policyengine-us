from policyengine_us.model_api import *


class ar_medical_expense_deduction_indiv(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Arkansas medical and dental expense deduction when married filing separately"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=21"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        agi = add(tax_unit, period, ["ar_agi_indiv"])
        floor = tax_unit("ar_medical_expense_deduction_floor", period)
        medical_expenses = tax_unit("itemized_medical_expenses", period)
        return max_(0, medical_expenses - floor * agi)
