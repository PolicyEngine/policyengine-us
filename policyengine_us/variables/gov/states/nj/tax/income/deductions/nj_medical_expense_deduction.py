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
        "deducted separately. Premium inputs follow payer attribution: each "
        "person reports the premiums they paid, including family coverage "
        "regardless of who is covered. Each dependent's exclusion is limited "
        "to that dependent's own medical premiums. A dependent aggregate ALD "
        "override must identify the corresponding person ALDs for exclusion; "
        "the total alone does not establish which person paid the premiums."
    )
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
        # each dependent's deduction only to that person's own paid premiums.
        person = tax_unit.members
        excluded_dependent_premiums = tax_unit.sum(
            person("self_employed_health_insurance_ald_excluded_premiums", period)
            * person("is_tax_unit_dependent", period)
        )
        medical_expenses = (
            tax_unit("itemized_medical_expenses", period) - excluded_dependent_premiums
        )
        agi = tax_unit("nj_agi", period)
        floor = p.rate * agi
        applicable_medical_expenses = max_(0, medical_expenses - floor)
        return self_employed_medical_expense_deduction + applicable_medical_expenses
