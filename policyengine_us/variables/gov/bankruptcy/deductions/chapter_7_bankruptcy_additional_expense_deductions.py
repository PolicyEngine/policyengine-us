from policyengine_us.model_api import *


class chapter_7_bankruptcy_additional_expense_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "Chapter 7 Bankruptcy additional expense deductions"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=6"

    def formula(spm_unit, period, parameters):
        health_insurance_expense = add(
            spm_unit, period, ["health_insurance_premiums"]
        )
        health_savings_account_expense = add(
            spm_unit, period, ["health_savings_account_payroll_contributions"]
        )

        care_expense = add(spm_unit, period, ["care_expenses"])
        home_energy_costs = spm_unit.household(
            "current_home_energy_use", period
        )
        education_expense = add(spm_unit, period, ["k12_tuition_and_fees"])
        child_count = add(spm_unit, period, ["is_child_dependent"])
        p = parameters(period).gov.bankruptcy.expenses
        education_expense_allowance = child_count * p.dependent_expense
        adjust_education_expense = min_(
            education_expense, education_expense_allowance
        )

        charitable_contributions = add(
            spm_unit,
            period,
            ["charitable_cash_donations", "charitable_non_cash_donations"],
        )
        return (
            health_insurance_expense
            + health_savings_account_expense
            + care_expense
            + home_energy_costs
            + adjust_education_expense
            + charitable_contributions
        )
