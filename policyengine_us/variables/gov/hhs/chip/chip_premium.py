from policyengine_us.model_api import *


STATE_CHIP_PREMIUM_VARIABLES = [
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
        "on cost sharing. PolicyEngine currently applies this cap to modeled "
        "premiums and enrollment fees only; because CHIP copayments, "
        "deductibles, coinsurance, and similar charges are not modeled here, "
        "this can under-enforce the combined cost-sharing cap."
    )
    definition_period = YEAR
    reference = "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-D/part-457/subpart-E/section-457.560"

    def formula(tax_unit, period, parameters):
        uncapped_premium = add(tax_unit, period, STATE_CHIP_PREMIUM_VARIABLES)
        p = parameters(period).gov.hhs.chip.cost_sharing.cap
        family_income = max_(0, tax_unit("medicaid_magi", period))
        return min_(uncapped_premium, family_income * p.rate)
