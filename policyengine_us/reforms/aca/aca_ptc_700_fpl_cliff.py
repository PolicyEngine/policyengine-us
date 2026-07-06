from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_aca_ptc_700_fpl_cliff() -> Reform:
    class aca_required_contribution_percentage(Variable):
        """
        ACA required contribution percentage with amended rate schedule extended to 700% FPL.

        This reform extends ACA premium subsidies to 700% FPL with the following
        amended contribution schedule:

        Under this reform:
        - 0-150% FPL: 0% contribution
        - 150-200% FPL: 0-2% contribution
        - 200-250% FPL: 2-4% contribution
        - 250-300% FPL: 4-6% contribution
        - 300-400% FPL: 6-8.5% contribution
        - 400-600% FPL: 8.5% contribution (flat)
        - 600-700% FPL: 8.5-9.25% contribution
        - Above 700% FPL: No subsidy eligibility
        """

        value_type = float
        entity = TaxUnit
        label = "ACA required contribution percentage with 700% FPL cliff (i.e., IRS Form 8962 'applicable figure')"
        unit = "/1"
        definition_period = YEAR
        reference = [
            "26 U.S. Code § 36B(b)(3)(A) - Refundable credit for coverage under a qualified health plan",
            "https://www.law.cornell.edu/uscode/text/26/36B#b_3_A",
        ]

        def formula(tax_unit, period, parameters):
            magi_frac = tax_unit("aca_magi_fraction", period)
            p = parameters(period).gov.contrib.aca.ptc_700_fpl_cliff.brackets
            return np.interp(magi_frac, p.thresholds, p.amounts)

    class is_aca_ptc_eligible(Variable):
        """
        Extended ACA PTC eligibility up to 700% FPL.
        """

        value_type = bool
        entity = Person
        label = "Person is eligible for ACA premium tax credit and pays ACA premium"
        definition_period = YEAR

        def formula(person, period, parameters):
            # Reuse baseline status, coverage, and premium-paying eligibility
            # so that all minimum-essential-coverage exclusions encoded in
            # gov.aca.ineligible_coverage (Basic Health Program, Oregon
            # Healthier Oregon, VA/CHAMPVA/TRICARE, Medicaid work-requirement,
            # etc.) continue to block the reform, and married-filing-separately
            # remains ineligible.
            fstatus = person.tax_unit("filing_status", period)
            separate = fstatus == fstatus.possible_values.SEPARATE

            # Override only income eligibility to use the reform's 700% FPL
            # bracket, preserving the baseline below-FPL immigration exception.
            p = parameters(period).gov.contrib.aca.ptc_700_fpl_cliff
            magi_frac = person.tax_unit("aca_magi_fraction", period)
            standard_income_eligible = p.income_eligibility.calc(magi_frac)
            below_fpl_exception = person.tax_unit(
                "aca_ptc_below_fpl_immigration_exception", period
            )
            is_income_eligible = standard_income_eligible | below_fpl_exception

            return person("pays_aca_premium", period) & ~separate & is_income_eligible

    class reform(Reform):
        def apply(self):
            self.update_variable(aca_required_contribution_percentage)
            self.update_variable(is_aca_ptc_eligible)

    return reform


def create_aca_ptc_700_fpl_cliff_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_aca_ptc_700_fpl_cliff()

    p = parameters.gov.contrib.aca.ptc_700_fpl_cliff
    current_period = period_(period)

    # Check if reform is active within a 5-year lookahead window
    reform_active = False
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_aca_ptc_700_fpl_cliff()
    else:
        return None


aca_ptc_700_fpl_cliff = create_aca_ptc_700_fpl_cliff_reform(None, None, bypass=True)
