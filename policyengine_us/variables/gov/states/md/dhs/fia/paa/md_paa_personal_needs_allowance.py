from policyengine_us.model_api import *


class md_paa_personal_needs_allowance(Variable):
    value_type = float
    entity = Person
    label = "Maryland PAA personal needs allowance"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.04",
        "https://dhs.maryland.gov/documents/FIA/Action%20Transmittals-AT%20-%20Information%20Memo-IM/AT-IM2023/23-02%20AT%20-%20COLA%20Mass%20Mod%20FFY23.pdf#page=3",
        "https://dhs.maryland.gov/documents/FIA/Action%20Transmittals-AT%20-%20Information%20Memo-IM/AT-IM2026/26-04%20IM%202025%20PNA%20Increase.pdf#page=2",
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20900%20Calculation%20of%20Benefits%20rev%2011.22.docx",
    )
    adds = ["gov.states.md.dhs.fia.paa.personal_needs_allowance"]
