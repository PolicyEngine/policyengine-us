from policyengine_us.model_api import *


class pa_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF"
    unit = USD
    definition_period = MONTH
    defined_for = "pa_tanf_eligible"
    reference = (
        "https://www.pa.gov/agencies/dhs/resources/cash-assistance/tanf",
        "http://services.dpw.state.pa.us/oimpolicymanuals/cash/137_Cash_Initiatives/137.4_Work_Expense_Reimbursement.htm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf.income.work_expense

        maximum_benefit = spm_unit("pa_tanf_maximum_benefit", period)
        countable_income = spm_unit("pa_tanf_countable_income", period)

        benefit = max_(maximum_benefit - countable_income, 0)
        # Cap benefit at maximum to prevent negative income
        # from inflating benefits above the maximum.
        return min_(benefit, maximum_benefit)
