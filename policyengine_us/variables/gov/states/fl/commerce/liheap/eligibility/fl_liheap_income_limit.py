from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class fl_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Florida LIHEAP annual heating maximum income value before rounding"
    defined_for = StateCode.FL
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/FL_Plan_2026.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/FL_BenefitMatrix_Heat-Cool_2026.pdf",
        "https://liheapch.acf.gov/delivery/income_eligibility.htm",
        "https://liheapch.acf.gov/docs/2025/state-plans/FL_Plan_2025.pdf#page=8",
        "https://liheapch.acf.gov/docs/2025/benefits-matricies/FL_BenefitMatrix_2025.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.commerce.liheap.eligibility
        size = spm_unit("fl_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        size_smi = smi(size, state, period, parameters)
        if p.truncates_smi_limit:
            four_person_smi = parameters(period).gov.hhs.smi.amount[state]
            size_share = size_smi / four_person_smi
            # This floor order reconciles all FY2026 matrix rows for sizes 1-12;
            # the sources do not expressly prescribe the rounding order.
            four_person_limit = np.floor(four_person_smi * p.smi_rate)
            smi_limit = np.floor(four_person_limit * size_share)
        else:
            # The FY2025 matrix rounds this unrounded amount, and each band
            # cutoff derived from it, to the nearest dollar.
            smi_limit = size_smi * p.smi_rate
        # Source conflict: manual 900.01D (page 39) sets 60% of SMI for sizes
        # 1-8 and 150% of the poverty guideline for 9 or more, while 1100.03D
        # (page 47) and 1200.01A (page 49) set 150% of the guideline for every
        # size. The FY2025 plan and matrix match 900.01D. The FY2026 plan
        # (page 8) and matrix use 60% of SMI for every size, and the manual
        # says to follow DEO's current benefit matrix (page 9), so FY2026
        # follows the matrix.
        # The printed FY2026 size-13 maximum, $157,686, equals 100% of SMI.
        # Apply the plan's explicit 60% eligibility rule ($94,610); payment
        # bands remain the published matrix row in fl_liheap. The federal
        # table restricts its 150%-FPG large-household exception to
        # cooling/crisis. Larger sizes follow the federal factors without table
        # verification.
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        limit = max_(smi_limit, guideline * p.fpg_rate)
        return where(size > 0, limit, 0)
