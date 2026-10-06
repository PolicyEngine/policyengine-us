from policyengine_us.model_api import *


class nj_liheap_income_band(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP payment income band"
    defined_for = StateCode.NJ
    reference = (
        "https://nj.gov/dca/dhcr/offices/docs/FY2026%20Benefit%20Matrix.pdf",
        # PDF pages 7, 9, 12.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=7",
    )
    documentation = (
        "The grid does not label the income period; monthly follows the handbook "
        "income test and the historical monthly thresholds used in the grid. Three "
        "identical initial rows are combined."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.dca.liheap.payment
        monthly = spm_unit("nj_liheap_countable_income", period) / MONTHS_IN_YEAR
        return p.income_band.calc(max_(monthly, 0))
