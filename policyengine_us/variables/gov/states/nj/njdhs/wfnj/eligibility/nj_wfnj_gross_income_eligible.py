from policyengine_us.model_api import *


class nj_wfnj_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Jersey WFNJ gross income eligible"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-3",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.wfnj
        gross_income = spm_unit("nj_wfnj_gross_income", period)
        payment_levels = spm_unit("nj_wfnj_payment_levels", period)
        max_allowable = np.round(payment_levels * p.income.limit)
        return gross_income <= max_allowable
