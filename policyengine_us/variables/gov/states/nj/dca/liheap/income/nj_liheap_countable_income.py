from policyengine_us.model_api import *


class nj_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP annualized household income"
    unit = USD
    defined_for = StateCode.NJ
    reference = (
        # PDF pages 6, 9, 10.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=9",
        # PDF pages 6, 10, 11.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2027%20LIHEAP%20Handbook.pdf#page=10",
    )
    documentation = (
        "Annual inputs approximate the four-week verification period. The summed "
        "monthly income is rounded to the nearest dollar, with half dollars rounded "
        "up. WFNJ benefits are counted once at the unit level. Every per-person "
        "source is floored at zero, so a rental or farm-rent loss does not offset "
        "other income."
    )

    def formula(spm_unit, period, parameters):
        # The annual TANF aggregate applies take-up to WFNJ entitlement.
        # Benefits received are counted once at the household level.
        income = add(spm_unit, period, ["nj_liheap_countable_income_person", "tanf"])
        # Handbook 2.3.F (page 9): "Cents shall be rounded to the nearest
        # dollar"; an exact half dollar rounds up.
        return np.floor(max_(income, 0) / MONTHS_IN_YEAR + 0.5) * MONTHS_IN_YEAR
