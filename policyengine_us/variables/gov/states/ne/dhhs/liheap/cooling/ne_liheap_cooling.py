from policyengine_us.model_api import *


class ne_liheap_cooling(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nebraska LIHEAP regular cooling assistance"
    documentation = (
        "Verified for FY2026 (the June-August 2026 cooling season). Earlier "
        "years use model parameter backfilling and are unverified historical "
        "estimates. Later years carry the FY2026 cooling table forward until a "
        "new table is added."
    )
    defined_for = "ne_liheap_cooling_eligible"
    reference = (
        "https://dhhs.ne.gov/Documents/Low%20Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29%20Guidance%20Document%202026.pdf#page=3",
        # 476 NAC 3-001 and 3-003.01, PDF pages 1-2
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/chapter-pdfs/476%20NAC%203%20(12-26-2020).pdf/1748#page=1",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/chapter-pdfs/476%20NAC%201%20(12-26-2020).pdf/1746#page=1",
        "https://dhhs.ne.gov/Pages/Energy-Assistance.aspx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.liheap.cooling
        income_ratio = spm_unit("ne_liheap_payment_fpg_ratio", period)
        dwelling = spm_unit("ne_liheap_dwelling_type", period)
        multifamily = dwelling == dwelling.possible_values.MULTI_FAMILY
        # The cooling season runs June 1 through August 31 (476 NAC 1-004.04),
        # and DHHS pays "one time per cooling season" (Energy Assistance page).
        # The FY2026 table has no fuel column. No FY2026 cooling supplement has
        # been verified.
        return where(
            multifamily,
            p.multifamily.calc(income_ratio, right=True),
            p.single_family.calc(income_ratio, right=True),
        )
