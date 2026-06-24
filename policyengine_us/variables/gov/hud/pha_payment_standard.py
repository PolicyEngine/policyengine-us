from policyengine_us.model_api import *


class pha_payment_standard(Variable):
    value_type = float
    entity = Household
    label = "HUD payment standard"
    unit = USD
    documentation = "Payment standard for HUD programs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/982.503"

    def formula(household, period, parameters):
        # Resolve the payment standard from most to least geographically
        # specific: a PHA's published ZIP-level standard, then the metro Small
        # Area FMR, then the LA County local schedule, then the county FMR as a
        # national proxy. The ZIP-level paths only fire on a match, so
        # households without a covered ZIP fall back unchanged.
        # https://www.lacda.org/docs/librariesprovider25/section-8-program/shared-document---payment-standard---vash/hcv-ehv-vash-payment-standards.pdf
        household_bedrooms = household("bedrooms", period)
        is_sro = household("is_sro", period)
        in_la = household("in_la", period)
        hud_fair_market_rent = household("hud_fair_market_rent", period)
        zip_code_payment_standard = household("zip_code_payment_standard", period)
        small_area_fair_market_rent = household("small_area_fair_market_rent", period)
        safmr_used_for_hcv = household("safmr_used_for_hcv", period)
        la_amount = select(
            [
                is_sro,
                household_bedrooms == 0,
                household_bedrooms == 1,
                household_bedrooms == 2,
                household_bedrooms == 3,
                household_bedrooms == 4,
                household_bedrooms == 5,
                household_bedrooms == 6,
                household_bedrooms == 7,
            ],
            [1_380, 1_840, 2_096, 2_666, 3_465, 3_804, 4_374, 4_945, 5_515],
            default=6_086,  # 8 bedrooms
        )
        la_payment_standard = la_amount * MONTHS_IN_YEAR
        county_or_la = where(in_la, la_payment_standard, hud_fair_market_rent)
        # Use the metro SAFMR only where it is the designated HCV basis (the
        # mandatory-SAFMR metros), not merely wherever a SAFMR value exists.
        metro_or_county = where(
            safmr_used_for_hcv,
            small_area_fair_market_rent,
            county_or_la,
        )
        return where(
            zip_code_payment_standard > 0,
            zip_code_payment_standard,
            metro_or_county,
        )
