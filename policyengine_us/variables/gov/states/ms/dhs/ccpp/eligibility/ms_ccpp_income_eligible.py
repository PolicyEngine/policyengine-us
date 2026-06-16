from policyengine_us.model_api import *


class ms_ccpp_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Mississippi CCPP based on income"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=26"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.ccpp.income
        countable_income = spm_unit("ms_ccpp_countable_income", period)
        # hhs_smi is annual; reading it with the monthly period auto-converts.
        monthly_smi = spm_unit("hhs_smi", period)
        return countable_income <= monthly_smi * p.smi_rate
