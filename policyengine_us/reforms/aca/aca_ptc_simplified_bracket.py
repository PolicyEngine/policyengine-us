from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_aca_ptc_simplified_bracket() -> Reform:
    class aca_required_contribution_percentage(Variable):
        """
        ACA Premium Tax Credit phase-out rate with simplified linear progression.

        This reform creates a single linear phase-out starting at 100% FPL,
        where the contribution percentage increases by 4 percentage points
        per 100% FPL increment. This results in a simpler, more aggressive
        phase-out compared to the additional bracket reform.

        The reform eliminates the standard ACA bracket structure entirely,
        replacing it with one continuous linear progression from 100% FPL
        onwards.

        Related issue: https://github.com/PolicyEngine/policyengine-us/issues/6629
        """

        value_type = float
        entity = TaxUnit
        label = "ACA PTC phase-out rate with simplified bracket (i.e., IRS Form 8962 'applicable figure')"
        unit = "/1"
        definition_period = YEAR
        reference = [
            "26 U.S. Code § 36B(b)(3)(A) - Refundable credit for coverage under a qualified health plan",
            "https://www.law.cornell.edu/uscode/text/26/36B#b_3_A",
        ]

        def formula(tax_unit, period, parameters):
            magi_frac = tax_unit("aca_magi_fraction", period)
            p = parameters(
                period
            ).gov.contrib.aca.ptc_simplified_bracket.brackets
            return np.interp(magi_frac, p.thresholds, p.amounts)

    class is_aca_ptc_eligible(Variable):
        """
        Extended ACA PTC eligibility beyond 400% FPL.
        """

        value_type = bool
        entity = Person
        label = "Person is eligible for ACA premium tax credit and pays ACA premium"
        definition_period = YEAR

        def formula(person, period, parameters):
            # determine status eligibility for ACA PTC
            fstatus = person.tax_unit("filing_status", period)
            separate = fstatus == fstatus.possible_values.SEPARATE
            immigration_eligible = person(
                "is_aca_ptc_immigration_status_eligible", period
            )
            taxpayer_has_itin = person.tax_unit("taxpayer_has_itin", period)
            is_status_eligible = (
                taxpayer_has_itin & ~separate & immigration_eligible
            )

            # determine coverage eligibility for ACA plan
            INELIGIBLE_COVERAGE = [
                "is_medicaid_eligible",
                "is_chip_eligible",
                "is_aca_eshi_eligible",
                "is_medicare_eligible",
            ]
            is_coverage_eligible = (
                add(person, period, INELIGIBLE_COVERAGE) == 0
            )

            # determine income eligibility for ACA PTC (using reform parameter)
            p = parameters(period).gov.contrib.aca.ptc_simplified_bracket
            magi_frac = person.tax_unit("aca_magi_fraction", period)
            is_income_eligible = p.income_eligibility.calc(magi_frac)

            # determine which people pay an age-based ACA plan premium
            p_aca = parameters(period).gov.aca
            is_aca_adult = person("age", period) > p_aca.slcsp.max_child_age
            child_pays = (
                person("aca_child_index", period) <= p_aca.max_child_count
            )
            pays_aca_premium = is_aca_adult | child_pays

            return (
                is_status_eligible
                & is_coverage_eligible
                & is_income_eligible
                & pays_aca_premium
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(aca_required_contribution_percentage)
            self.update_variable(is_aca_ptc_eligible)

    return reform


def create_aca_ptc_simplified_bracket_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_aca_ptc_simplified_bracket()

    p = parameters.gov.contrib.aca.ptc_simplified_bracket
    current_period = period_(period)

    # Check if reform is active within a 5-year lookahead window
    # This allows the reform to be selected in the web app interface
    # even if it's scheduled to start in a future year
    reform_active = False
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_aca_ptc_simplified_bracket()
    else:
        return None


aca_ptc_simplified_bracket = create_aca_ptc_simplified_bracket_reform(
    None, None, bypass=True
)
