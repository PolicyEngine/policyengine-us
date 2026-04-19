from policyengine_us.model_api import *


class chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "CHIP premium"
    unit = USD
    documentation = (
        "Annual out-of-pocket Children's Health Insurance Program premium or "
        "enrollment fee paid by the tax unit. Federal default is zero; "
        "state-specific variables add the household-side cost where states "
        "charge one, subject to the federal 5 percent of family income cap "
        "on cost sharing."
    )
    definition_period = YEAR
    reference = "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-D/part-457/subpart-E/section-457.560"
    adds = [
        "al_chip_premium",
        "ct_chip_premium",
        "de_chip_premium",
        "fl_chip_premium",
        "ga_chip_premium",
        "ia_chip_premium",
        "id_chip_premium",
        "il_chip_premium",
        "in_chip_premium",
        "ks_chip_premium",
        "la_chip_premium",
        "ma_chip_premium",
        "mi_chip_premium",
        "mo_chip_premium",
        "ny_chip_premium",
        "tx_chip_premium",
        "wi_chip_premium",
    ]
