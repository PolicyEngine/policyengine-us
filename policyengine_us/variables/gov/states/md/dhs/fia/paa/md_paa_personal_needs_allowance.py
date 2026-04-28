from policyengine_us.model_api import *


class md_paa_personal_needs_allowance(Variable):
    value_type = float
    entity = Person
    label = "Maryland PAA personal needs allowance"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20900%20Calculation%20of%20Benefits%20rev%2011.22.docx",
        "https://dhs.maryland.gov/documents/FIA/Action%20Transmittals-AT%20-%20Information%20Memo-IM/AT-IM2026/26-04%20IM%202025%20PNA%20Increase.pdf#page=2",
    )

    def formula(person, period, parameters):
        return parameters(period).gov.states.md.dhs.fia.paa.personal_needs_allowance
