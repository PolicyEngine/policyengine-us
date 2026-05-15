from policyengine_us.model_api import *


class al_ccsp_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alabama CCSP based on income"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = (
        "Alabama CCDF State Plan 2025-2027, Section 2.2.4",
        "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=24",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhr.ccsp.eligibility
        monthly_income = spm_unit("al_ccsp_countable_income", period)
        annual_income = monthly_income * MONTHS_IN_YEAR

        # FPL test: 180% initial, 200% continuing (NJ pattern).
        fpg = spm_unit("spm_unit_fpg", period.this_year)
        enrolled = spm_unit("al_ccsp_enrolled", period)
        fpl_limit_ratio = where(
            enrolled,
            p.income_limit_fpl_continuing,
            p.income_limit_fpl_initial,
        )
        fpl_eligible = annual_income <= fpg * fpl_limit_ratio

        # Federal CCDF 85% SMI hard cap applies in both initial and
        # continuing tiers.
        smi = spm_unit("hhs_smi", period.this_year)
        smi_eligible = annual_income <= smi * p.income_limit_smi_cap

        return fpl_eligible & smi_eligible
