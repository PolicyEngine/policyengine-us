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
            p = parameters(period).gov.contrib.aca.ptc_700_fpl_cliff
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


def create_aca_ptc_700_fpl_cliff_reform(
    parameters, period, bypass: bool = False
):
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


aca_ptc_700_fpl_cliff = create_aca_ptc_700_fpl_cliff_reform(
    None, None, bypass=True
)
