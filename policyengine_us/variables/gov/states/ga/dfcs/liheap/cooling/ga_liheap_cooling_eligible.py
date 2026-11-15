from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ga.dfcs.liheap.eligibility._ga_liheap_housing import (
    ga_liheap_has_direct_payment_route,
)


class ga_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Georgia LIHEAP regular cooling assistance"
    defined_for = StateCode.GA
    reference = (
        # FY2026 state plan sections 3.1-3.5: 60% of state median income, no
        # additional eligibility requirements, no asset test, the first 30 days
        # for older and homebound residents, and the account-credit rule.
        # PDF pages 10-11
        "https://liheapch.acf.gov/docs/2026/state-plans/GA_Plan_2026.pdf#page=10",
        # PAMMS chapter 100, export dated 2026-11-04: cooling applicants "must
        # meet the eligibility requirements set forth for the current fiscal
        # year's Heating Program".
        "https://pamms.dhs.ga.gov/dfcs/_exports/liheap.pdf#page=4",
        "https://dfcs.georgia.gov/document/document/liheap-cooling-faq-fy2022/download#page=1",
        # Manual section 1300.2 pays "eligible individuals whose heating or
        # cooling costs are included in their rent and designated as a separate
        # cost"; the rental agreement is assumed to designate it, as heating
        # assumes the agreement is verified. The energy burden table pays
        # unsubsidized rent that includes heat and electric directly to the
        # applicant.
        # PDF pages 70, 89
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=70",
        # DHS 2026 cooling release: applicants provide the "Most recent cooling
        # bill or statement of service from their energy providers".
        "https://dhs.georgia.gov/press-releases/2026-04-06/liheap-cooling-open",
    )

    def formula(spm_unit, period, parameters):
        # Heating's household size and income tests apply. The energy burden is
        # the household's own cooling cost or the heating program's direct
        # payment route: unsubsidized rent that includes all utilities.
        # The matrix prints one cooling amount per level for every main heating
        # fuel, so the fuel does not affect eligibility; paying a home with no
        # heating reads that single cooling cell as covering it.
        # Not modeled: the first 30 days reserved for residents 65 and older and
        # the medically homebound (plan items 3.3 and 3.4), funding on a
        # "first-come, first-served basis until all funds are exhausted" (DHS
        # 2026 release) and targeting when funding is too limited (PAMMS
        # page 4). The household's account is assumed to meet the $1,000
        # account-credit rule (plan item 3.5).
        cooling_cost = spm_unit("has_cooling_expense", period)
        all_utilities_in_rent = ga_liheap_has_direct_payment_route(spm_unit, period)
        return (
            (spm_unit("ga_liheap_household_size", period) > 0)
            & spm_unit("ga_liheap_income_eligible", period)
            & (cooling_cost | all_utilities_in_rent)
        )
