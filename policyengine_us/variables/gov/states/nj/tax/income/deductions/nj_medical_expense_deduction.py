from policyengine_us.model_api import *


class nj_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey medical expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    reference = (
        "https://pub.njleg.gov/bills/9899/PL99/222_.HTM",
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
        # C.54A:3-3 excludes premiums counted by the separate SE deduction
        # under C.54A:3-5, including dependents' deductions recognized by NJ.
        # The federal base already excludes the filers' deduction. Apply
        # dependents' deductions only to their own premium pool.
        dependent_premiums = tax_unit.sum(
            tax_unit.members("medical_expense_health_insurance_premiums", period)
            * tax_unit.members("is_tax_unit_dependent", period)
        )
        dependent_deduction = tax_unit(
            "dependents_self_employed_health_insurance_ald", period
        )
        excluded_dependent_premiums = min_(
            dependent_premiums, max_(0, dependent_deduction)
        )
        medical_expenses = (
            tax_unit("itemized_medical_expenses", period) - excluded_dependent_premiums
        )
        agi = tax_unit("nj_agi", period)
        floor = p.rate * agi
        applicable_medical_expenses = max_(0, medical_expenses - floor)
        return self_employed_medical_expense_deduction + applicable_medical_expenses
