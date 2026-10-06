from policyengine_us.model_api import *


class nj_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey medical expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.deductions.medical_expenses
        # nj_agi counts every member's income, dependents included, so the
        # dependents' self-employed health insurance deductions count too.
        self_employed_medical_expense_deduction = add(
            tax_unit,
            period,
            [
                "self_employed_health_insurance_ald",
                "dependents_self_employed_health_insurance_ald",
            ],
        )
        medical_expenses = tax_unit("itemized_medical_expenses", period)
        agi = tax_unit("nj_agi", period)
        floor = p.rate * agi
        applicable_medical_expenses = max_(0, medical_expenses - floor)
        return self_employed_medical_expense_deduction + applicable_medical_expenses
