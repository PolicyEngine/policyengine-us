from policyengine_us.model_api import *


class additonal_expenses_deductions(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Additional expenses deductions"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=6"
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        health_insurance_expense = add(spm_unit, period,["health_insurance_premiums"])
        health_savings_account_expense = add(spm_unit, period,["health_savings_account_payroll_contributions"])
        
        care_expense = add(spm_unit, period, ["care_expeses"])
        home_energy_costs = spm_unit.household("current_home_energy_use", period)
        education_expense = add(spm_unit, period, ["k12_tuition_and_fees"]) ## no more than $189.58 
        charitable_contributions = add(
                spm_unit,
                period,
                ["charitable_cash_donations", "charitable_non_cash_donations"],
            )
        total = health_insurance_expense + health_savings_account_expense + care_expense + home_energy_costs + education_expense + charitable_contributions
        return total/MONTHS_IN_YEAR
