from policyengine_us.model_api import *


class wa_pte_assessor_approved_value(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = (
        "Assessor-approved Washington property value before the regular levy exemption"
    )
    quantity_type = STOCK
    definition_period = YEAR
    default_value = -1
    defined_for = StateCode.WA
    reference = (
        "https://lawfilesext.leg.wa.gov/biennium/2023-24/Htm/Bills/Session%20Laws/House/1355-S.SL.htm",  # RCW 84.36.381(6) as applicable to 2025 collection
        "https://app.leg.wa.gov/WAC/default.aspx?cite=458-16A-140",  # (7)
    )
