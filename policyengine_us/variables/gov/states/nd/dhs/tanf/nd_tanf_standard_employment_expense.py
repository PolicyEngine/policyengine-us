from policyengine_us.model_api import *


class nd_tanf_standard_employment_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota TANF standard employment expense allowance"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40019/400_19_05.htm",
        "https://www.nd.gov/dhs/policymanuals/40019/400_19_110_20.htm",
    )
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.tanf.income.deductions
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        percentage_amount = gross_earned * p.standard_employment_expense.rate
        return max_(percentage_amount, p.standard_employment_expense.minimum)
