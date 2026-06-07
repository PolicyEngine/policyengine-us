from policyengine_us.model_api import *


class al_ccsp_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alabama CCSP based on income"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=24"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhr.ccsp.income.limit
        monthly_income = spm_unit("al_ccsp_countable_income", period)

        # Alabama's published income tables (Child Care Fact Sheet) use the
        # prior calendar year's HHS poverty guidelines throughout the
        # benefit year, since HHS publishes the new guidelines mid-January.
        annual_fpg = spm_unit("spm_unit_fpg", period.last_year)
        monthly_fpg = annual_fpg / MONTHS_IN_YEAR
        enrolled = spm_unit("al_ccsp_enrolled", period)
        fpl_limit_ratio = where(
            enrolled,
            p.fpl_continuing,
            p.fpl_initial,
        )
        fpl_eligible = monthly_income <= monthly_fpg * fpl_limit_ratio

        monthly_smi = spm_unit("hhs_smi", period)
        smi_eligible = monthly_income <= monthly_smi * p.smi_cap

        return fpl_eligible & smi_eligible
