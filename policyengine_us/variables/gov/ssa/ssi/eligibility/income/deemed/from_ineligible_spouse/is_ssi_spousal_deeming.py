from policyengine_us.model_api import *


class is_ssi_spousal_deeming(Variable):
    value_type = bool
    entity = Person
    label = "SSI spousal deeming applies"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"
    documentation = """
    Returns True when spousal deeming applies according to 20 CFR §416.1163.

    Spousal deeming applies when:
    1. Person is an eligible individual (not part of an eligible couple)
    2. Spouse is ineligible (not aged/blind/disabled)
    3. Spouse's leftover income (after child allocations) exceeds the difference
       between couple FBR and individual FBR

    When deeming applies, the benefit calculation uses the couple FBR instead
    of the individual FBR, recognizing that two people have higher expenses.
    """

    def formula(person, period, parameters):
        # Only applies to eligible individuals (not eligible spouses in a couple)
        is_eligible_individual = person("is_ssi_eligible_individual", period)

        # Get spouse's leftover income (after child allocations)
        spouse_earned = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spouse_unearned = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )
        leftover_spouse = spouse_earned + spouse_unearned

        # Compare to FBR differential (couple rate - individual rate)
        p = parameters(period).gov.ssa.ssi.amount
        diff = (p.couple - p.individual) * MONTHS_IN_YEAR

        # Deeming applies when leftover spouse income exceeds the differential
        # Note: regulation says "not more than" means ≤, so we use > for deeming
        return is_eligible_individual & (leftover_spouse > diff)
