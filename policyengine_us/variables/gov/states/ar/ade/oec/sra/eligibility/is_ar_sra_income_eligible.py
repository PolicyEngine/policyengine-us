from policyengine_us.model_api import *


class is_ar_sra_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income-eligible for Arkansas SRA"
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = "https://dese.ade.arkansas.gov/Files/2025-2027_CCDF_State_Plan_Final_4.26.24.1REV_OEC.pdf#page=22"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.eligibility
        monthly_income = spm_unit("ar_sra_countable_income", period)
        monthly_smi_limit = (
            spm_unit("hhs_smi", period.this_year) * p.income_smi_rate / MONTHS_IN_YEAR
        )
        return monthly_income <= monthly_smi_limit
