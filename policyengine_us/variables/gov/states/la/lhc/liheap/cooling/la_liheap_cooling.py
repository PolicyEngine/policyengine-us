from policyengine_us.model_api import *


class la_liheap_cooling(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Louisiana LIHEAP regular cooling assistance"
    defined_for = "la_liheap_cooling_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/LA_BenefitMatrix_Heat-Cool_2026.pdf",
        # PDF pages 43-44, 48
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20FINAL%20-%20Effective%20April%201%2c%202026.pdf#page=43",
        # PDF pages 4, 12
        "https://liheapch.acf.gov/docs/2026/state-plans/LA_Plan_2026.pdf#page=4",
    )
    # Section 4.2 B allows "one Heating and one Cooling LIHEAP benefit each
    # Program year", both from the Heating and Cooling Benefit Matrix, with no
    # bill cap. Annual bills stand in for the cooling-season bill, so the
    # burden band is the one heating uses. Supplemental cooling payments
    # depend on available funds and are not modeled.
    adds = ["la_liheap_matrix_amount"]
