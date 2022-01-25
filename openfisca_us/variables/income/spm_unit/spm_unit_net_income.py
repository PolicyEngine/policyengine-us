from openfisca_us.model_api import *


class spm_unit_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Net income"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        PERSONAL_INCOME_COMPONENTS = [
            "employment_income",
            "self_employment_income",
            "dividend_income",
            "interest_income",
            "ssdi",
        ]
        SPMU_INCOME_COMPONENTS = [
            "snap",
            "school_meal_subsidy",
            "wic",
            "ssi",
            "tanf",
        ]
        SPMU_EXPENSE_COMPONENTS = [
            "spm_unit_fica",
            "spm_unit_federal_tax",
            "spm_unit_state_tax",
            "spm_unit_capped_work_childcare_expenses",
            "spm_unit_medical_expenses",
        ]
        personal_income = aggr(spm_unit, period, PERSONAL_INCOME_COMPONENTS)
        spmu_income = add(spm_unit, period, SPMU_INCOME_COMPONENTS)
        spmu_expense = add(spm_unit, period, SPMU_EXPENSE_COMPONENTS)
        return personal_income + spmu_income - spmu_expense
