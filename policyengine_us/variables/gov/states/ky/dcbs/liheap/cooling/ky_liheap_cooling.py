from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg
from policyengine_us.variables.gov.states.ky.dcbs.liheap.ky_liheap import (
    ky_liheap_points_amount,
)


class ky_liheap_cooling(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Kentucky LIHEAP regular cooling assistance"
    documentation = (
        "One-time electric cooling subsidy per federal fiscal year. Verified "
        "for FY2026; other years use model parameter backfilling and are "
        "unverified estimates."
    )
    defined_for = "ky_liheap_cooling_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/KY_BenefitMatrix_Heat-Cool_2026.xlsx",
        # PDF pages 4,10-11: Sections 1.1, 3.4-3.6.
        "https://liheapch.acf.gov/docs/2026/state-plans/KY_Plan_2026.pdf#page=4",
        "https://www.capky.org/wp-content/uploads/2026/07/FY26-LIHEAP-Summer-Cooling-Subsidy-Fact-Sheet.pdf",
        # Section 4(3).
        "https://apps.legislature.ky.gov/law/kar/titles/921/004/116/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.dcbs.liheap
        size = spm_unit("spm_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)
        # The income bands use the cooling guideline year, like the income
        # limit, so the top band ends at the limit.
        guideline = fpg(
            max_(size, 1),
            state_group,
            period,
            parameters,
            year_lag=p.cooling.fpg_year_lag,
        )
        # Cooling assistance provides electric benefits only (plan Section
        # 3.4). The FY2026 workbook's cooling column equals its electricity
        # heating column in every row, so the electric fuel points apply
        # whatever fuel heats the home.
        return ky_liheap_points_amount(
            spm_unit,
            period,
            parameters,
            p.payment.fuel_points.ELECTRICITY,
            guideline,
        )
