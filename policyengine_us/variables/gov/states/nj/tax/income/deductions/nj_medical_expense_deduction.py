from policyengine_us.model_api import *


class nj_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey medical expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nj.tax.income.deductions.medical_expenses
        self_employed_medical_expense_deduction = tax_unit(
            "self_employed_health_insurance_ald", period
        )
        medical_expenses = add(
            tax_unit, period, ["medical_out_of_pocket_expenses"]
        )
        agi = tax_unit("nj_agi", period)
        floor = p.rate * agi
        applicable_medical_expenses = max_(0, medical_expenses - floor)
        return (
            self_employed_medical_expense_deduction
            + applicable_medical_expenses
        )
