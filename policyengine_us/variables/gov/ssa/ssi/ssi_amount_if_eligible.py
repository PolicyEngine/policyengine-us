from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_living_arrangement_amount import (
    ssi_living_arrangement_amount,
)


class ssi_amount_if_eligible(Variable):
    value_type = float
    entity = Person
    label = "SSI amount if eligible"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/42/1382#b"

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi.amount

        # 20 CFR 416.414(b): Benefit rate depends on couple computation:
        # 1. Couple computation applies → couple rate / 2 per person
        # 2. No couple computation, deeming → couple rate (limited by
        #    416.1163(e)(2) in uncapped_ssi)
        # 3. No couple computation, no deeming → individual rate
        #
        # ssi_couple_computation_applies is false when only one spouse
        # is in a medical facility (416.414(b)(3)), even if both are
        # SSI-eligible. ssi_claim_is_joint remains true for state SSPs.

        couple_computation = person("ssi_couple_computation_applies", period)
        deeming_applies = person("is_ssi_spousal_deeming_applies", period.this_year)

        individual_or_deeming_amount = where(
            deeming_applies,
            p.couple,
            p.individual,
        )

        base_amount = where(
            couple_computation,
            p.couple / 2,
            individual_or_deeming_amount,
        )

        # Children (under 18) always receive individual FBR. A child never
        # files a joint claim with parents — joint claims are between
        # spouses only. Adults 18+ (including students) go through normal
        # couple/deeming logic since they may be married.
        base_amount = where(
            person("is_child", period.this_year), p.individual, base_amount
        )

        return ssi_living_arrangement_amount(person, period, parameters, base_amount)
