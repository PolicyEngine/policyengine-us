from policyengine_us.model_api import *


class ar_liheap_cooling(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Arkansas LIHEAP summer regular cooling benefit"
    defined_for = "ar_liheap_cooling_eligible"
    reference = (
        # FFY 2025 manual section 6.1: the Electricity Matrix is "used for both
        # Winter and Summer Regular Assistance". No FY2026 manual was found.
        "https://liheapch.acf.gov/docs/2025/manuals/AR_Manual_2025.pdf#page=78",
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2026_Electric.pdf#page=1",
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2025_Electric.pdf#page=1",
        # FY2026 state plan section 3.6: cooling benefits of $60 to $344.
        "https://liheapch.acf.gov/docs/2026/state-plans/AR_Plan_2026.pdf#page=13",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ee.aeo.liheap.payment
        income = spm_unit("ar_liheap_countable_income", period) / MONTHS_IN_YEAR
        size = spm_unit("ar_liheap_household_size", period)
        band = p.income_band.calc(max_(income, 0)).astype(int)
        size_group = p.household_size_group.calc(size).astype(int)
        # One fixed grant per summer from the Electricity matrix, the same for
        # every heating type, not capped at the bill. The planned FY2027
        # increase has no posted matrix, so later years carry the FY2026 cells
        # forward.
        return p.matrix.electricity[band][size_group]
