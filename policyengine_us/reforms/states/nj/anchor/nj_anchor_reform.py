from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_nj_anchor() -> Reform:
    class nj_anchor(Variable):
        value_type = float
        entity = TaxUnit
        label = "New Jersey ANCHOR benefit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.nj.gov/treasury/taxation/anchor/",
            "https://www.nj.gov/treasury/taxation/anchor/calculated.shtml",
        )
        defined_for = "nj_anchor_eligible"

        def formula(tax_unit, period, parameters):
            p_baseline = parameters(period).gov.states.nj.tax.income.credits.anchor
            p_reform = parameters(period).gov.contrib.states.nj.anchor

            gross_income = add(tax_unit, period, ["nj_gross_income"])
            greater_age = tax_unit("greater_age_head_spouse", period)
            is_senior = greater_age >= p_baseline.age_threshold

            pays_property_taxes = add(tax_unit, period, ["real_estate_taxes"]) > 0
            pays_rent = tax_unit("rents", period)
            is_homeowner = pays_property_taxes & ~pays_rent
            is_renter = pays_rent & ~pays_property_taxes

            lower_income = gross_income <= p_baseline.homeowner.income_limit.lower

            if p_reform.in_effect:
                senior_lower = p_reform.homeowner.senior.amount.lower_income
                senior_upper = p_reform.homeowner.senior.amount.upper_income
            else:
                senior_lower = p_baseline.homeowner.senior.amount.lower_income
                senior_upper = p_baseline.homeowner.senior.amount.upper_income

            homeowner_senior_amount = where(lower_income, senior_lower, senior_upper)

            # Non-senior homeowner amounts: unchanged from baseline
            homeowner_non_senior_amount = where(
                lower_income,
                p_baseline.homeowner.non_senior.amount.lower_income,
                p_baseline.homeowner.non_senior.amount.upper_income,
            )
            homeowner_amount = where(
                is_senior,
                homeowner_senior_amount,
                homeowner_non_senior_amount,
            )

            # Renter amounts: unchanged from baseline
            renter_amount = where(
                is_senior,
                p_baseline.renter.senior.amount,
                p_baseline.renter.non_senior.amount,
            )

            return where(
                is_homeowner,
                homeowner_amount,
                where(is_renter, renter_amount, 0),
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(nj_anchor)

    return reform


def create_nj_anchor_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_nj_anchor()

    p = parameters.gov.contrib.states.nj.anchor

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_nj_anchor()
    else:
        return None


nj_anchor_budget_reform = create_nj_anchor_reform(None, None, bypass=True)
