from policyengine_us.model_api import *


class la_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Louisiana LIHEAP regular heating assistance"
    documentation = (
        "Louisiana's single regular heating-season award from the FFY2026 "
        "Heating and Cooling Benefit Matrix: an amount by energy burden, on a "
        "total-energy-cost basis, and household size, plus one priority group "
        "supplement, whose disability group also covers Social Security "
        "disability benefits and SSI receipt. Verified for FY2026; earlier "
        "and later years are unverified estimates through "
        "parameter backfilling. Louisiana also pays one regular cooling-season "
        "benefit each program year from the same matrix, la_liheap_cooling; "
        "crisis assistance and weatherization are out of scope."
    )
    defined_for = "la_liheap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/LA_BenefitMatrix_Heat-Cool_2026.pdf",
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20REVISED%20January%201_%202024.pdf#page=41",
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20FINAL%20-%20Effective%20April%201%2c%202026.pdf#page=48",
        "https://liheapch.acf.gov/docs/2026/state-plans/LA_Plan_2026.pdf#page=10",
    )
    # One award covers the heating season, with no bill cap. Supplemental
    # heating payments depend on available funds and are not modeled.
    adds = ["la_liheap_matrix_amount"]
