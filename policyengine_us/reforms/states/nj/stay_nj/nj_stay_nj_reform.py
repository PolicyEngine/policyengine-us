from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_nj_stay_nj() -> Reform:
    class nj_staynj_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "New Jersey Stay NJ Property Tax Credit program eligibility"
        definition_period = YEAR
        reference = (
            "https://pub.njleg.state.nj.us/Bills/2022/PL23/75_.HTM",
            "https://www.nj.gov/treasury/taxation/staynj/index.shtml",
        )
        defined_for = StateCode.NJ

        def formula(tax_unit, period, parameters):
            p_baseline = parameters(period).gov.states.nj.tax.income.credits.staynj
            p_reform = parameters(period).gov.contrib.states.nj.stay_nj

            greater_age = tax_unit("greater_age_head_spouse", period)
            age_eligible = greater_age >= p_baseline.age_threshold

            gross_income = add(tax_unit, period, ["nj_gross_income"])
            if p_reform.in_effect:
                income_eligible = gross_income < p_reform.income_limit
            else:
                income_eligible = gross_income < p_baseline.income_limit

            pays_property_taxes = add(tax_unit, period, ["real_estate_taxes"]) > 0
            pays_rent = tax_unit("rents", period)
            is_homeowner = pays_property_taxes & ~pays_rent

            return age_eligible & income_eligible & is_homeowner

    class nj_staynj(Variable):
        value_type = float
        entity = TaxUnit
        label = "New Jersey Stay NJ Property Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://pub.njleg.state.nj.us/Bills/2022/PL23/75_.HTM",
            "https://www.nj.gov/treasury/taxation/staynj/index.shtml",
        )
        defined_for = "nj_staynj_eligible"

        def formula(tax_unit, period, parameters):
            p_baseline = parameters(period).gov.states.nj.tax.income.credits.staynj
            p_reform = parameters(period).gov.contrib.states.nj.stay_nj

            property_taxes = add(tax_unit, period, ["real_estate_taxes"])

            if p_reform.in_effect:
                max_benefit = p_reform.max_benefit
            else:
                max_benefit = p_baseline.max_benefit
            target_benefit = min_(property_taxes * p_baseline.rate, max_benefit)

            anchor_benefit = tax_unit("nj_anchor", period)
            senior_freeze = tax_unit("nj_senior_freeze", period)

            return max_(target_benefit - anchor_benefit - senior_freeze, 0)

    class reform(Reform):
        def apply(self):
            self.update_variable(nj_staynj_eligible)
            self.update_variable(nj_staynj)

    return reform


def create_nj_stay_nj_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_nj_stay_nj()

    p = parameters.gov.contrib.states.nj.stay_nj

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_nj_stay_nj()
    else:
        return None


nj_stay_nj_budget_reform = create_nj_stay_nj_reform(None, None, bypass=True)
