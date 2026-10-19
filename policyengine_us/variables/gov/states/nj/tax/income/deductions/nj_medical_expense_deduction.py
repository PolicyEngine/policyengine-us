from policyengine_us.model_api import *


class nj_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey medical expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    documentation = (
        "New Jersey's separate self-employed health insurance deduction plus "
        "medical expenses above the state floor, excluding premiums already "
        "deducted separately. Worksheet F counts medical expenses the filers "
        "paid for themselves and their dependents. Premium inputs follow payer "
        "attribution: each person reports the premiums they paid, including "
        "family coverage regardless of who is covered. So the head's and "
        "spouse's premiums count, and a dependent's own premium payments, "
        "after-tax or through payroll, do not."
    )
    reference = (
        "https://pub.njleg.gov/bills/9899/PL99/222_.HTM",
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
        # Worksheet F line 1 takes medical expenses the filers paid for
        # themselves and their dependents. The federal base counts the
        # head's and spouse's premiums net of their self-employed deduction
        # (C.54A:3-3 excludes premiums deducted separately) and leaves out a
        # dependent's own premium payments, including any the dependent
        # deducted as self-employed.
        # New Jersey includes salary-reduction cafeteria-plan premiums in
        # taxable wages (TB-39(R)), so the filers' own payroll premiums also
        # qualify. The separate payroll input is disjoint from the after-tax
        # premium inputs and, like them, sits on the person who paid.
        filer_payroll_premiums = tax_unit_non_dep_sum(
            "pre_tax_health_insurance_premiums", tax_unit, period
        )
        medical_expenses = (
            tax_unit("itemized_medical_expenses", period) + filer_payroll_premiums
        )
        agi = tax_unit("nj_agi", period)
        floor = p.rate * agi
        applicable_medical_expenses = max_(0, medical_expenses - floor)
        return self_employed_medical_expense_deduction + applicable_medical_expenses
