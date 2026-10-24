from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.model_api import *


class is_ssi_spousal_deeming_applies_monthly(Variable):
    value_type = bool
    entity = Person
    label = "SSI spousal deeming applies"
    definition_period = MONTH
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
        supplied = annual_input(person, period, "is_ssi_spousal_deeming_applies")
        if supplied is not None:
            return supplied

        # Get spouse's deemed income (after child allocations)
        spouse_deemed_income = add(
            person,
            period,
            [
                "ssi_earned_income_deemed_from_ineligible_spouse_monthly",
                "ssi_unearned_income_deemed_from_ineligible_spouse_monthly",
            ],
        )

        # Compare to FBR differential (couple rate - individual rate)
        p = parameters(period).gov.ssa.ssi.amount
        diff = p.couple - p.individual

        # Deeming applies when spouse's deemed income exceeds the differential
        # Note: regulation says "not more than" means ≤, so we use > for deeming
        return person("is_ssi_eligible_individual", period) & (
            spouse_deemed_income > diff
        )
