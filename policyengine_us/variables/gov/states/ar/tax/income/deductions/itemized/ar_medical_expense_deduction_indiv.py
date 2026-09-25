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
        p = parameters(
            period
        ).gov.states.ar.tax.income.deductions.itemized.medical_expense
        agi = add(tax_unit, period, ["ar_agi_indiv"])
        # "You or your spouse" (AR3 Line 3B): check the whole marital unit, so a
        # spouse filing a separate return still counts.
        person = tax_unit.members
        couple_max_age = person.marital_unit.max(person("age", period))
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        senior = tax_unit.any(
            head_or_spouse & (couple_max_age >= p.senior.age_threshold)
        )
        floor = where(senior, p.senior.income_floor, p.income_floor)
        medical_expenses = tax_unit("itemized_medical_expenses", period)
        return max_(0, medical_expenses - floor * agi)
