from policyengine_us.model_api import *


class fl_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TANF payment standard"
    unit = USD
    definition_period = YEAR
    reference = "Florida Statute § 414.095(10)"
    documentation = "Payment standard based on family size and shelter tier, before family cap adjustments"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.dcf.tanf.payment_standard

        family_size = spm_unit.nb_persons()
        shelter_tier = spm_unit("fl_tanf_shelter_tier", period)

        # Get payment standard for each tier using calc()
        tier_1_amount = p.tier_1.calc(family_size)
        tier_2_amount = p.tier_2.calc(family_size)
        tier_3_amount = p.tier_3.calc(family_size)

        # Select monthly payment based on shelter tier
        monthly_payment = select(
            [shelter_tier == 1, shelter_tier == 2, shelter_tier == 3],
            [tier_1_amount, tier_2_amount, tier_3_amount],
        )

        return monthly_payment * MONTHS_IN_YEAR
