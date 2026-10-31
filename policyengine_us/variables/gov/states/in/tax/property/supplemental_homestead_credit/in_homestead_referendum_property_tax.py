from policyengine_us.model_api import *


class in_homestead_referendum_property_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana referendum property tax on the qualifying homestead"
    documentation = (
        "The part of in_homestead_property_tax_liability imposed after approval "
        "by the voters in a referendum or local public question."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # IC 6-1.1-20.6-7.7(d), added by SEA 1 (2025), SECTION 74
        "https://iga.in.gov/pdf-documents/124/2025/senate/bills/SB0001/SB0001.05.ENRH.pdf#page=124",
        # DLGF June 18, 2025 FAQ, question 30
        "https://www.in.gov/dlgf/files/2025-presentations/250618-FAQ-Webinar-Legislative-Update.pdf#page=8",
    )
