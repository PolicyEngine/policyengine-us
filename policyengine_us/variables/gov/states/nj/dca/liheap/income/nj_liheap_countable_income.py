from policyengine_us.model_api import *


class nj_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP annualized household income"
    unit = USD
    defined_for = StateCode.NJ
    reference = (
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=6,9,10",
    )
    documentation = "Annual inputs approximate the four-week verification period. The summed monthly income is rounded to the nearest dollar, with half dollars rounded up. WFNJ benefits are counted once at the unit level; rental income is assumed nonnegative."

    def formula(spm_unit, period, parameters):
        # WFNJ paid for eligible household members is counted once, in full.
        income = add(spm_unit, period, ["nj_liheap_countable_income_person", "nj_wfnj"])
        return np.floor(max_(income, 0) / MONTHS_IN_YEAR + 0.5) * MONTHS_IN_YEAR
