from policyengine_us.model_api import *


class wa_millionaires_tax_base_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington millionaires tax base income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=7",
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=11",
    )
    defined_for = "wa_millionaires_tax_applies"
    adds = ["adjusted_gross_income"]
