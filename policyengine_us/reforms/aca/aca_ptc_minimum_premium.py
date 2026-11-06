from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_aca_ptc_minimum_premium() -> Reform:
    class aca_ptc_minimum_premium(Variable):
        value_type = float
        entity = TaxUnit
        label = "ACA minimum premium for tax unit"
        unit = USD
        definition_period = YEAR
        documentation = (
            "The part of the tax unit's enrolled premiums the premium tax credit "
            "cannot cover: the monthly minimum times 12, once for a tax unit with "
            "any member eligible for the credit. The January 2026 CARE Act draft "
            "(section 5(a)(1)) reduces the monthly premiums in 26 U.S.C. "
            "36B(b)(2)(A), for the plans covering the taxpayer, spouse and "
            "dependents, by $5. Zero in years the reform is not in effect."
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.aca.minimum_premium
            has_enrollee = add(tax_unit, period, ["is_aca_ptc_eligible"]) > 0
            return where(p.in_effect & has_enrollee, p.amount * MONTHS_IN_YEAR, 0)

    class aca_ptc_before_filing_gate(Variable):
        value_type = float
        entity = TaxUnit
        label = "ACA premium tax credit before the filing condition"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/36B#b"
        documentation = (
            "The benchmark premium less the required contribution, but no more "
            "than the enrolled premium less the minimum premium. The enrolled "
            "premium is the selected plan's premium, or the benchmark premium "
            "when that is higher, since the credit is otherwise computed as if "
            "the tax unit enrolled in the benchmark plan; used_aca_ptc applies "
            "the cap for a cheaper selected plan."
        )
        defined_for = "is_aca_ptc_eligible"

        def formula(tax_unit, period, parameters):
            return 0

        def formula_2018(tax_unit, period, parameters):
            plan_cost = tax_unit("slcsp", period)
            income = tax_unit("aca_magi", period)
            applicable_figure = tax_unit("aca_required_contribution_percentage", period)
            credit = max_(0, plan_cost - income * applicable_figure)
            enrolled_premium = max_(
                plan_cost,
                tax_unit("selected_marketplace_plan_premium_proxy", period),
            )
            minimum = tax_unit("aca_ptc_minimum_premium", period)
            return min_(credit, max_(0, enrolled_premium - minimum))

    class used_aca_ptc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Used ACA premium tax credit"
        unit = USD
        definition_period = YEAR
        documentation = (
            "The premium tax credit applied to the selected plan, which leaves "
            "the minimum premium to pay on that plan."
        )

        def formula(tax_unit, period, parameters):
            plan_premium = tax_unit("selected_marketplace_plan_premium_proxy", period)
            minimum = tax_unit("aca_ptc_minimum_premium", period)
            return min_(
                tax_unit("aca_ptc", period),
                max_(0, plan_premium - minimum),
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(aca_ptc_minimum_premium)
            self.update_variable(aca_ptc_before_filing_gate)
            self.update_variable(used_aca_ptc)

    return reform


def create_aca_ptc_minimum_premium_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_aca_ptc_minimum_premium()

    p = parameters.gov.contrib.aca.minimum_premium
    current_period = period_(period)

    # Check if reform is active within a 5-year lookahead window
    reform_active = False
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_aca_ptc_minimum_premium()
    else:
        return None


aca_ptc_minimum_premium = create_aca_ptc_minimum_premium_reform(None, None, bypass=True)
