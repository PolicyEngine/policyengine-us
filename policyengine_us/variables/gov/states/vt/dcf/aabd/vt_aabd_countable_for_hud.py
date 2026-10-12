from policyengine_us.model_api import *


class vt_aabd_countable_for_hud(Variable):
    value_type = float
    entity = Person
    label = "Vermont AABD countable for HUD"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://www.ecfr.gov/current/title-24/section-5.609",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf",
    )
    documentation = "Applies 24 CFR 5.609(b)(19) to Essential Person care payments enabling a disabled family member to remain at home. This is an interpretation of the federal exclusion and the certified care purpose in Vermont rule 2781, not an express Vermont HUD instruction. Ordinary aged-person income support remains countable. Override if the housing agency determines a different countable amount or disability status."

    def formula(person, period, parameters):
        disabled = person("is_disabled", period.this_year) | person(
            "is_blind", period.this_year
        )
        return person("vt_aabd_federal", period) + ~disabled * person(
            "vt_aabd_ep", period
        )
