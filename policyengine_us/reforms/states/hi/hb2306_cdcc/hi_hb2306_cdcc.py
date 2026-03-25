from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_hi_hb2306_cdcc() -> Reform:
    """
    Hawaii HB 2306 HD1 CDCC Rate Reform.

    This reform implements the expanded CDCC (Child and Dependent Care Credit)
    rate schedule proposed in HB 2306 for taxable years beginning after
    December 31, 2026.

    The bill increases the applicable percentage of employment-related
    expenses from the current maximum of 25% to 50%, with a more gradual
    phase-down extending to higher AGI levels ($160,000+).

    Reference: https://www.capitol.hawaii.gov/sessions/session2026/bills/HB2306_HD1_.HTM
    """

    class hi_cdcc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Hawaii child and dependent care credit"
        defined_for = "hi_cdcc_eligible"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.capitol.hawaii.gov/sessions/session2026/bills/HB2306_HD1_.HTM"
        )

        def formula(tax_unit, period, parameters):
            p_reform = parameters(period).gov.contrib.states.hi.hb2306.cdcc

            # Calculate smaller of dependent care benefits and minimum earnings
            smaller_of_benefits_and_earnings = min_(
                tax_unit("hi_dependent_care_benefits", period),
                tax_unit("hi_cdcc_min_head_spouse_earned", period),
            )
            min_earned = max_(0, smaller_of_benefits_and_earnings)

            # Get AGI for rate calculation
            agi = tax_unit("hi_agi", period)

            rate = p_reform.rate.calc(agi, right=True)

            return rate * min_earned

    class reform(Reform):
        def apply(self):
            self.update_variable(hi_cdcc)

    return reform


def create_hi_hb2306_cdcc_reform(parameters, period, bypass: bool = False):
    """
    Factory function to create the HB 2306 CDCC reform.

    Args:
        parameters: PolicyEngine parameters object
        period: The tax period
        bypass: If True, always return the reform (for testing)

    Returns:
        The reform class if active, None otherwise
    """
    if bypass:
        return create_hi_hb2306_cdcc()

    p = parameters.gov.contrib.states.hi.hb2306.cdcc

    reform_active = False
    current_period = period_(period)

    # Check if reform is active in current or next 5 years
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_hi_hb2306_cdcc()
    else:
        return None


# Instantiate the reform for direct import
hi_hb2306_cdcc = create_hi_hb2306_cdcc_reform(None, None, bypass=True)
