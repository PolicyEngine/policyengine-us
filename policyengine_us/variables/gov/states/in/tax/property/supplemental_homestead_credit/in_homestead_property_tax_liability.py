from policyengine_us.model_api import *


class in_homestead_property_tax_liability(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana property tax liability on the qualifying homestead"
    documentation = (
        "Property tax first due and payable for the year on the homestead that "
        "receives the IC 6-1.1-12-37 standard deduction, after the credits "
        "applied before the supplemental homestead credit (including the "
        "Over 65 and Blind/Disabled credits) and before the supplemental "
        "homestead credit. Excludes tax on any other property."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # IC 6-1.1-20.6-7.7(c)(1)(A), added by SEA 1 (2025), SECTION 74
        "https://iga.in.gov/pdf-documents/124/2025/senate/bills/SB0001/SB0001.05.ENRH.pdf#page=124",
        # DLGF June 18, 2025 FAQ, questions 27, 29 and 33 (order of operations)
        # PDF pages 7-9
        "https://www.in.gov/dlgf/files/2025-presentations/250618-FAQ-Webinar-Legislative-Update.pdf#page=7",
    )
