from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit, smi
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
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        "https://floridaliheap.com/faq",
        # PDF pages 9, 11-12
        "https://www.pbcgov.com/pubInf/Agenda/20260106/3E2.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.commerce.liheap.eligibility
        size = spm_unit("fl_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        if p.truncates_smi_limit:
            # The HHS floor order reconciles all FY2026 matrix rows, sizes 1-12.
            smi_limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        else:
            # The FY2025 matrix rounds this unrounded amount, and each band
            # cutoff derived from it, to the nearest dollar.
            smi_limit = smi(size, state, period, parameters) * p.smi_rate
        # Source conflict: manual 900.01D (page 39) sets 60% of SMI for sizes
        # 1-8 and 150% of the poverty guideline for 9 or more, while 1100.03D
        # (page 47) and 1200.01A (page 49) set 150% of the guideline for every
        # size. The FY2025 plan and matrix match 900.01D. The FY2026 plan
        # (page 8) and matrix use 60% of SMI for every size, and the manual
        # says to follow DEO's current benefit matrix (page 9), so FY2026
        # follows the matrix. The October 2025 subgrant contract conflicts too:
        # G(7)d (page 12) sets 150% of the poverty guideline for every size and
        # G(8)c (page 12) 150% of the guideline from 9 people, but G(1) (page
        # 11) and D(10)b (page 9) defer to the Commerce payment matrix.
        # The printed FY2026 size-13 row tops out at $157,686, which is 100% of
        # SMI (103,063 x 1.53), and the portal FAQ prints $13,141 a month
        # (157,686 / 12). The matrix footnote says 60% of SMI, plan item 2.1
        # (page 8) lists 60% for sizes 1-9, and 42 U.S.C. 8624(b)(2)(B) caps
        # eligibility at the greater of 150% of poverty and 60% of SMI, which
        # the printed row exceeds. Size 13 therefore uses 60% of SMI ($94,610)
        # for both this limit and the payment bands. The federal table
        # restricts its 150%-FPG large-household exception to cooling/crisis.
        # Larger sizes follow the federal factors without table verification;
        # from 15 people the 110%-of-poverty floor in fl_liheap_eligible
        # exceeds this limit.
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        limit = max_(smi_limit, guideline * p.fpg_rate)
        return where(size > 0, limit, 0)
