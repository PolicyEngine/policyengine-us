from policyengine_us.model_api import *


class al_tanf_self_employment_net_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF Self-Employment Net Income"
    defined_for = StateCode.AL
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        # Getting the gross income of self-employed persons
        self_employment_income = add(
            spm_unit, period, ["self_employment_income"]
        )
        # Using the self employment deduction rate
        p = parameters(period).gov.states.al.dhs.tanf.income
        # Calculating self-employment operating costs.
        operating_expenses = (
            self_employment_income * p.self_employment_deduction_rate
        )
        # Add the misc_deduction variable
        misc_deductions = add(spm_unit, period, ["misc_deduction"])
        # Calculating and return net self-employment income
        return self_employment_income - operating_expenses - misc_deductions
