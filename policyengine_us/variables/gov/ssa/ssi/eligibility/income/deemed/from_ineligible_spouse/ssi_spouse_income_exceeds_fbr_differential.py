from policyengine_us.model_api import *


class ssi_spouse_income_exceeds_fbr_differential(Variable):
    value_type = bool
    entity = Person
    label = "Spouse's leftover income exceeds SSI FBR differential"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"
    documentation = """
    Checks whether the ineligible spouse's leftover income (after child allocations) 
    is above the difference between the couple and individual FBR. If not, no deeming.
    """

    def formula(person, period, parameters):
        # Summation of spouse’s leftover after child allocations
        # We already have these stored in ssi_earned_income_deemed_from_ineligible_spouse
        # and ssi_unearned_income_deemed_from_ineligible_spouse
        leftover = add(
            person,
            period,
            [
                "ssi_earned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
            ],
        )

        # Compute difference between couple FBR and individual FBR
        p = parameters(period).gov.ssa.ssi.amount
        diff_annual = (p.couple - p.individual) * MONTHS_IN_YEAR

        return leftover > diff_annual
