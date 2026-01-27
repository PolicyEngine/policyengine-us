from policyengine_us.model_api import *


class nj_wfnj_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Jersey WFNJ income eligible"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-1",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-3",
    )

    def formula(spm_unit, period, parameters):
        is_enrolled = spm_unit("is_tanf_enrolled", period)
        gross_income_eligible = spm_unit(
            "nj_wfnj_gross_income_eligible", period
        )
        countable_income = spm_unit("nj_wfnj_countable_income", period)
        payment_levels = spm_unit("nj_wfnj_payment_levels", period)
        countable_income_eligible = countable_income < payment_levels

        # Enrolled: countable income test only
        # Not enrolled: both gross income AND countable income tests
        return where(
            is_enrolled,
            countable_income_eligible,
            gross_income_eligible & countable_income_eligible,
        )
