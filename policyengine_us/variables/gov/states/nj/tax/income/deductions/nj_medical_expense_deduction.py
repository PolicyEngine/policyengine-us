from policyengine_us.model_api import *


class nj_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey medical expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    reference = (
        "https://www.nj.gov/treasury/taxation/njit13.shtml",
        "https://www.nj.gov/treasury/taxation/pdf/pubs/tb/tb39r.pdf#page=1",
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=25",
    )

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
        # New Jersey includes salary-reduction cafeteria-plan premiums in
        # taxable wages (TB-39(R)), so these employee-paid premiums also
        # qualify for the medical expense deduction. The separate payroll
        # input is disjoint from the after-tax premium inputs.
        medical_expenses = tax_unit("itemized_medical_expenses", period) + add(
            tax_unit, period, ["pre_tax_health_insurance_premiums"]
        )
        agi = tax_unit("nj_agi", period)
        floor = p.rate * agi
        applicable_medical_expenses = max_(0, medical_expenses - floor)
        return self_employed_medical_expense_deduction + applicable_medical_expenses
