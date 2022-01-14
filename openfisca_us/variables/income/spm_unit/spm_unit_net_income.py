from openfisca_us.model_api import *


class spm_unit_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit net income"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        INCOME_COMPONENTS = [
            "spm_unit_total_income",
            "snap",
            "spm_unit_capped_housing_subsidy",
            "spm_unit_school_lunch_subsidy",
            "spm_unit_energy_subsidy",
            "spm_unit_wic",
        ]
        EXPENSE_COMPONENTS = [
            "spm_unit_fica",
            "spm_unit_federal_tax",
            "spm_unit_state_tax",
            "spm_unit_capped_work_childcare_expenses",
            "spm_unit_medical_expenses",
        ]
        income = add(spm_unit, period, *INCOME_COMPONENTS)
        expense = add(spm_unit, period, *EXPENSE_COMPONENTS)
        return income - expense
