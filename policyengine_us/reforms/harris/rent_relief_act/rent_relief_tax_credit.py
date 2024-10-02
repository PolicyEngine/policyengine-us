from policyengine_us.model_api import *


def create_rent_relief_tax_credit() -> Reform:
    class rent_relief_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rent Relief Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.congress.gov/bill/116th-congress/senate-bill/1106/text"

        def formula(tax_unit, period, parameters):
            # The applicable rent amount is capped at fair market rent
            rent = add(tax_unit, period, ["rent"])
            p = parameters(
                period
            ).gov.contrib.harris.rent_relief_act.rent_relief_credit
            safmr = tax_unit.household("small_area_fair_market_rent", period)

            gross_income = add(tax_unit, period, ["irs_gross_income"])
            # Reduce the income (equivalent to raising thresholds) for households
            # in high income areas, as defined by using SAFMR for HCV.

            rent_cap = safmr * p.safmr_share_rent_cap
            capped_rent = min_(rent, rent_cap)
            gross_income_fraction = (
                p.rent_income_share_threshold * gross_income
            )
            rent_excess = max_(capped_rent - gross_income_fraction, 0)
            safmr_used_for_hcv = tax_unit.household(
                "safmr_used_for_hcv", period
            )
            high_income_reduction = (
                safmr_used_for_hcv * p.high_income_area_threshold_increase
            )
            applicable_gross_income = max_(
                gross_income - high_income_reduction, 0
            )
            applicable_percentage = p.applicable_percentage.calc(
                applicable_gross_income, right=True
            )
            amount_if_rent_not_subsidized = applicable_percentage * rent_excess
            housing_assistance = tax_unit.spm_unit(
                "housing_assistance", period
            )
            rent_is_subsidized = housing_assistance > 0
            reduced_rent = max_(0, rent - housing_assistance)
            amount_if_rent_subsidized = reduced_rent * p.subsidized_rent_rate
            return where(
                rent_is_subsidized,
                amount_if_rent_subsidized,
                amount_if_rent_not_subsidized,
            )

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.credits
            previous_credits = add(tax_unit, period, p.refundable)
            rent_relief_credit = tax_unit("rent_relief_tax_credit", period)
            return rent_relief_credit + previous_credits

    class reform(Reform):
        def apply(self):
            self.update_variable(rent_relief_tax_credit)
            self.update_variable(income_tax_refundable_credits)

    return reform


def create_rent_relief_tax_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_rent_relief_tax_credit()

    p = parameters(
        period
    ).gov.contrib.harris.rent_relief_act.rent_relief_credit

    if p.in_effect:
        return create_rent_relief_tax_credit()
    else:
        return None


rent_relief_tax_credit = create_rent_relief_tax_credit_reform(
    None, None, bypass=True
)
