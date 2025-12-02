from policyengine_us.model_api import *


class ssi_amount_if_eligible(Variable):
    value_type = float
    entity = Person
    label = "SSI amount if eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382#b"

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi.amount
        is_dependent = person("is_tax_unit_dependent", period)

        # Three scenarios for adults:
        # 1. Both spouses eligible (joint claim) → couple rate / 2
        # 2. One eligible, no deeming → individual rate
        # 3. One eligible, deeming applies → couple rate (capped in ssi)
        #
        # Note: In scenario 3, deeming applies when spouse's GROSS income > $483.
        # Income exclusions are applied to the COMBINED income afterwards.
        # This means countable income can be much lower than $483, and the
        # benefit can exceed individual FBR, requiring the cap in ssi.

        is_joint_claim = person("ssi_claim_is_joint", period)
        deeming_applies = person("is_ssi_spousal_deeming_applies", period)

        # Determine FBR to use based on scenario
        individual_or_deeming_amount = where(
            deeming_applies,
            p.couple,  # Scenario 3: Deeming applies - use couple rate!
            p.individual,  # Scenario 2: No deeming
        )

        head_or_spouse_amount = where(
            is_joint_claim,
            p.couple / 2,  # Scenario 1: Both eligible
            individual_or_deeming_amount,
        )

        # Adults amount is based on scenario (see above)
        # Dependents always use individual amount.
        ssi_per_month = where(
            is_dependent, p.individual, head_or_spouse_amount
        )
        return ssi_per_month * MONTHS_IN_YEAR
