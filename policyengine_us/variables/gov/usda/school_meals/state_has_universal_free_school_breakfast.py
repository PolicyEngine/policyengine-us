from policyengine_us.model_api import *


class state_has_universal_free_school_breakfast(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "State has universal free school breakfast"
    documentation = (
        "Whether the SPM unit lives in a state that offers free breakfast to "
        "all students regardless of household income. States that offer free "
        "breakfast and lunch to all students are in "
        "state_has_universal_free_school_meals."
    )
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/38-822.03",
        "https://www.legis.state.pa.us/WU01/LI/LI/US/HTM/2023/0/0033..HTM",
        "https://web.archive.org/web/20220917043427/https://www.governor.pa.gov/newsroom/gov-wolf-announces-universal-free-breakfast-program-for-1-7-million-pennsylvania-school-children/",
        "https://arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2025R%2FPublic%2FACT123.pdf#page=2",
        "https://legis.delaware.gov/SessionLaws/Chapter/GetPdfDocument?fileAttachmentId=650776#page=1",
        "https://legis.delaware.gov/SessionLaws/Chapter/GetPdfDocument?fileAttachmentId=650671#page=29",
        "https://www.scstatehouse.gov/sess126_2025-2026/appropriations2026/tap1b.htm#s1",
        # PDF pages 1, 7-8
        "https://portal.ct.gov/-/media/sde/nutrition/nslp/memos/om2023/om18-23.pdf#page=1",
        # PDF pages 1, 4
        "https://portal.ct.gov/-/media/sde/nutrition/nslp/memos/om2026/om13-26.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        state = spm_unit.household("state_code_str", period)
        return parameters(period).gov.usda.school_meals.state_universal_free_breakfast[
            state
        ]
