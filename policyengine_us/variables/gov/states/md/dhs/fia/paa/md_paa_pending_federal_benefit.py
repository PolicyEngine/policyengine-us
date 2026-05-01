from policyengine_us.model_api import *


class md_paa_pending_federal_benefit(Variable):
    value_type = bool
    entity = Person
    label = "Maryland PAA pending federal cash benefit applicant"
    documentation = (
        "True if the person has a pending SSI/SSDI/RSDI application or was "
        "denied a federal cash benefit through no fault of their own, "
        "qualifying for PAA under PAA Manual 300.5 / COMAR 07.03.07.03 "
        "while the federal claim is resolved."
    )
    definition_period = MONTH
    defined_for = StateCode.MD
    default_value = False
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20300%20Technical%20Eligibility%20rev%2011.22.docx",
        "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-07-03",
    )
