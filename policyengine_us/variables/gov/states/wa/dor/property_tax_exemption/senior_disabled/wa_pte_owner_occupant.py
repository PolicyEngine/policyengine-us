from policyengine_us.model_api import *


class wa_pte_owner_occupant(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Claimant owns and occupies the whole qualifying Washington principal residence"
    )
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://lawfilesext.leg.wa.gov/biennium/2023-24/Htm/Bills/Session%20Laws/House/1355-S.SL.htm",  # RCW 84.36.381(1) and (2) as applicable to 2025 collection
        "https://dor.wa.gov/sites/default/files/2022-02/64-0002.pdf#page=1",
    )
