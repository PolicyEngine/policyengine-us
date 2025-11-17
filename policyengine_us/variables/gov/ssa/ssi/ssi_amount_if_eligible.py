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
        # 3. One eligible, deeming applies → couple rate
        #
        # Note: In scenario 3, regulations specify a cap at individual FBR,
        # but this is mathematically impossible to trigger since:
        # - Deeming only applies when spouse's countable ≥ $483
        # - Benefit = couple FBR ($1,450) - combined countable
        # - Therefore: Benefit ≤ $1,450 - $483 = $967 (individual FBR)
        # No explicit cap logic is needed in uncapped_ssi.

        is_joint_claim = person("ssi_claim_is_joint", period)
        deeming_applies = person("ssi_spousal_deeming_applies", period)

        head_or_spouse_amount = where(
            is_joint_claim,
            p.couple / 2,  # Scenario 1: Both eligible
            where(
                deeming_applies,
                p.couple,  # Scenario 3: Deeming applies - use couple rate!
                p.individual,  # Scenario 2: No deeming
            ),
        )

        # Adults amount is based on scenario (see above)
        # Dependents always use individual amount.
        ssi_per_month = where(
            is_dependent, p.individual, head_or_spouse_amount
        )
        return ssi_per_month * MONTHS_IN_YEAR
