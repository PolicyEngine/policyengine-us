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
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=6",
    )
    documentation = "Annual inputs approximate the four-week verification period. The summed monthly income is rounded to the nearest dollar, with half dollars rounded up. WFNJ benefits are counted once at the unit level; rental income is assumed nonnegative."

    def formula(spm_unit, period, parameters):
        # The annual TANF aggregate applies take-up to WFNJ entitlement.
        # Benefits received are counted once at the household level.
        income = add(spm_unit, period, ["nj_liheap_countable_income_person", "tanf"])
        return np.floor(max_(income, 0) / MONTHS_IN_YEAR + 0.5) * MONTHS_IN_YEAR
