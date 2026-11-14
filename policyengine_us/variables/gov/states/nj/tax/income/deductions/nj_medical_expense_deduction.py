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
        "https://www.nj.gov/treasury/taxation/njit13.shtml",
        "https://www.nj.gov/treasury/taxation/pdf/pubs/tb/tb39r.pdf#page=1",
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=25",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.deductions.medical_expenses
        # The filers' own self-employed health insurance deduction. A
        # dependent's self-employment income and its deduction go on the
        # dependent's own return, as nj_agi leaves out the dependent's income.
        self_employed_medical_expense_deduction = tax_unit(
            "self_employed_health_insurance_ald", period
        )
        # C.54A:3-3 excludes premiums counted by the separate SE deduction
        # under C.54A:3-5, including a dependent's deduction on their own
        # return.
        # The computed federal base excludes each dependent's deduction.
        # Supplied subtotals retain the separate state medical exclusion.
        excluded_dependent_premiums = 0
        if has_input_for_period(
            tax_unit.simulation, "itemized_medical_expenses", period
        ):
            excluded_dependent_premiums = tax_unit(
                "itemized_medical_expenses_excluded_dependent_premiums", period
            )
        # New Jersey includes salary-reduction cafeteria-plan premiums in
        # taxable wages (TB-39(R)), so these employee-paid premiums also
        # qualify for the medical expense deduction. The separate payroll
        # input is disjoint from the after-tax premium inputs.
        medical_expenses = (
            tax_unit("itemized_medical_expenses", period)
            - excluded_dependent_premiums
            + add(tax_unit, period, ["pre_tax_health_insurance_premiums"])
        )
        agi = tax_unit("nj_agi", period)
        floor = p.rate * agi
        applicable_medical_expenses = max_(0, medical_expenses - floor)
        return self_employed_medical_expense_deduction + applicable_medical_expenses
