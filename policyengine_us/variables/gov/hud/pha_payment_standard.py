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
        # Only Los Angeles County for now.
        # https://www.lacda.org/docs/librariesprovider25/section-8-program/shared-document---payment-standard---vash/hcv-ehv-vash-payment-standards.pdf
        household_bedrooms = household("bedrooms", period)
        is_sro = household("is_sro", period)
        in_la = household("in_la", period)
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
        return in_la * la_amount * MONTHS_IN_YEAR
