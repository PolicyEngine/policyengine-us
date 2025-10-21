from policyengine_us.model_api import *


class fl_tanf_shelter_tier(Variable):
    value_type = int
    entity = SPMUnit
    label = "Florida TANF shelter tier"
    definition_period = MONTH
    reference = "Florida Statute § 414.095(10)"
    documentation = "Determines payment tier: 1 (no shelter), 2 (shelter $1-$50), or 3 (shelter >$50 or homeless)"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.dcf.tanf.payment_standard

        # Get shelter costs (rent + mortgage + property taxes)
        rent = spm_unit("rent", period)

        # Determine tier based on shelter obligation
        tier_2_min = p.tier_2_min_shelter
        tier_2_max = p.tier_2_max_shelter

        # Tier 1: No shelter obligation ($0)
        # Tier 2: Shelter $1-$50
        # Tier 3: Shelter >$50 or homeless
        tier = where(
            rent == 0,
            1,
            where(
                (rent >= tier_2_min) & (rent <= tier_2_max),
                2,
                3,
            ),
        )

        return tier
