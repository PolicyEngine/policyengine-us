from policyengine_us.model_api import *


class ut_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Utah CCAP income eligible"
    definition_period = MONTH
    defined_for = StateCode.UT
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-710"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.ccap.income
        countable_income = spm_unit("ut_ccap_countable_income", period)
        # Countable income, less applicable deductions, must be at or below
        # the Department's percentage of the state median income for the
        # household size (R986-700-710(6)(b)). hhs_smi is an annual dollar
        # amount, so reading it with the bare monthly period auto-divides it
        # to a monthly value.
        monthly_smi = spm_unit("hhs_smi", period)
        return countable_income <= monthly_smi * p.smi_rate
