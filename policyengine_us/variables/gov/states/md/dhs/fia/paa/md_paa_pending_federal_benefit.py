from policyengine_us.model_api import *


class md_paa_pending_federal_benefit(Variable):
    value_type = bool
    entity = Person
    label = "Maryland PAA pending federal cash benefit applicant"
    definition_period = MONTH
    defined_for = StateCode.MD
    default_value = False
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.03",
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20300%20Technical%20Eligibility%20rev%2011.22.docx",
    )
