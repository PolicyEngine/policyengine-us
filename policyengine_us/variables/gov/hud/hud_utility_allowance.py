from policyengine_us.model_api import *


class hud_utility_allowance(Variable):
    value_type = float
    entity = Household
    label = "HUD utility allowance"
    unit = USD
    documentation = "Utility allowance for HUD programs"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/24/982.517",
        # LA County, only one for now. As of 2023-07-01.
        "https://www.lacda.org/docs/librariesprovider25/public-documents/utility-allowance/utility-allownce-2022.pdf",
    )
    defined_for = "tenant_pays_utilities"

    def formula(household, period, parameters):
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
            # For LA County, assume all utilities are included.
            [
                179,  # SRO: 9 + 15 + 4 + 6 + 6 + 12 + 20 + 55 + 32 + 7 + 13
                227,  # 0bd: 9 + 16 + 5 + 8 + 8 + 16 + 27 + 73 + 42 + 10 + 13
                271,  # 1bd: 13 + 22 + 7 + 11 + 11 + 22 + 33 + 82 + 42 + 15 + 13
                318,  # 2bd: 16 + 29 + 9 + 15 + 15 + 29 + 40 + 91 + 42 + 19 + 13
                375,  # 3bd: 20 + 37 + 11 + 18 + 18 + 35 + 48 + 109 + 42 + 24 + 13
                452,  # 4bd: 27 + 50 + 14 + 23 + 25 + 44 + 55 + 127 + 42 + 32 + 13
                517,  # 5bd: 31 + 58 + 16 + 26 + 31 + 51 + 66 + 145 + 42 + 38 + 13
                580,  # 6bd: 37 + 65 + 18 + 29 + 36 + 58 + 75 + 163 + 42 + 44 + 13
                647,  # 7bd: 42 + 74 + 20 + 33 + 42 + 65 + 85 + 181 + 42 + 50 + 13
            ],
            default=719,  # 8bd: 47 + 86 + 24 + 36 + 47 + 73 + 96 + 199 + 42 + 56 + 13
        )
        return in_la * la_amount * MONTHS_IN_YEAR
