from policyengine_us.model_api import *


class assigned_co_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Assigned Colorado Premium Assistance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = (
        # Amended Regulation 4-2-78 (3 CCR 702-4), Section 5.B: Colorado
        # Premium Assistance is paid to enrolled members, so the modeled value
        # is gated on take-up (mirrors assigned_aca_ptc).
        "https://drive.google.com/file/d/1GkpvQTauvS4hr97_CSfkSEQCnoYjqrJI/view",
        "https://connectforhealthco.com/new-customers/tips-for-choosing-a-plan/colorado-premium-assistance/",
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("co_premium_assistance", period) * tax_unit(
            "takes_up_co_premium_assistance_if_eligible", period
        )
