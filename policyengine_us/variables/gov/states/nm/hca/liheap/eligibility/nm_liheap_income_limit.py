from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nm_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "New Mexico LIHEAP income limit"
    defined_for = StateCode.NM
    reference = (
        # 8.150.100.9 D NMAC
        "https://www.srca.nm.gov/parts/title08/08.150.0100.html",
        # 8.150.520.14 and 8.150.520.15 NMAC
        "https://www.srca.nm.gov/parts/title08/08.150.0520.html",
        "https://liheapch.acf.gov/docs/2026/state-plans/NM_Plan_2026.pdf#page=9",
        "https://www.hca.nm.gov/wp-content/uploads/DETAILED-MODEL-PLAN-LIHEAP_10_01_2026-4.pdf#page=8",
        "https://www.hca.nm.gov/wp-content/uploads/Heating-and-Cooling-Point-and-Income-Guide-2026.pdf",
        "https://www.hca.nm.gov/wp-content/uploads/NM-LIHEAP-FFY-2027-Point-and-Income-Guidelines.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.liheap.eligibility
        size = spm_unit("nm_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        # The rate is applied to the guideline for each household size and
        # the monthly amount is rounded to the nearest dollar, which
        # reproduces the guides' printed rows for sizes 1-8. For sizes 9 and
        # over, the guides' "each additional" increments can differ by $1 or
        # more a month, growing with size (FFY2026 size 9: $7,457 by
        # increment, $7,456 by rate).
        # Monthly income is tested, so the annual limit is 12 times the
        # monthly amount ($23,472 for one person in FFY2026); the FFY2026
        # guide's annual column prints 150% of the annual guideline ($23,475).
        monthly_limit = np.floor(guideline * p.fpg_rate / MONTHS_IN_YEAR + 0.5)
        return where(size > 0, monthly_limit * MONTHS_IN_YEAR, 0)
